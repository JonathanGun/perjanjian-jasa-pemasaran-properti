import abc
import enum
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload


class FileRole(enum.Enum):
    READER = "reader"
    WRITER = "writer"
    COMMENTER = "commenter"
    OWNER = "owner"


class StorageClient(abc.ABC):
    @abc.abstractmethod
    def upload(self, file_stream, filename, folder_id=None) -> str:
        pass

    @abc.abstractmethod
    def share(self, file_id, email, role=FileRole.READER):
        pass

    @abc.abstractmethod
    def download(self, file_id) -> io.BytesIO:
        pass

    @abc.abstractmethod
    def get_file_url(self, file_id):
        pass


class GoogleDriveClient(StorageClient):
    def __init__(self, service_account_file, scopes=None):
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/drive"]
        self.service_account_file = service_account_file
        self.scopes = scopes
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticate using a service account and return the Google Drive API service."""
        creds = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.scopes
        )
        return build("drive", "v3", credentials=creds)

    def upload(self, file_stream, filename, folder_id=None):
        """Upload a file to Google Drive."""
        file_metadata = {"name": filename}
        if folder_id:
            file_metadata["parents"] = [folder_id]
        media = MediaIoBaseUpload(file_stream, mimetype="application/pdf")
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return file.get("id")

    def share(self, file_id, email, role=FileRole.READER):
        """Share a file with a specific email."""
        if not email:
            raise ValueError("Email address is required")

        permission = {
            "type": "user",
            "role": role.value,
            "emailAddress": email,
        }
        self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields="id",
        ).execute()

    def _get_file_by_name(self, filename):
        """Get a file ID by its name."""
        query = f"name='{filename}'"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])
        if files:
            return files[0]  # Return the first match
        return None

    def get_file_url(self, filename):
        """Generate a sharable link for the file."""
        file_info = self._get_file_by_name(filename)
        if not file_info:
            raise FileNotFoundError(f"File not found: {filename}")

        file = (
            self.service.files()
            .get(fileId=file_info["id"], fields="webViewLink")
            .execute()
        )
        return file.get("webViewLink")

    def download(self, filename):
        """Download a file by its ID."""
        file_info = self._get_file_by_name(filename)
        if not file_info:
            raise FileNotFoundError(f"File not found: {filename}")

        request = self.service.files().get_media(fileId=file_info["id"])
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        file_stream.seek(0)
        return file_stream
