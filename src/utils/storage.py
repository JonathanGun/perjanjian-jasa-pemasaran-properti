import abc
import enum
import io
from typing import Dict, Optional
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload


class FileRole(enum.Enum):
    READER = "reader"
    WRITER = "writer"
    COMMENTER = "commenter"
    OWNER = "owner"


class StorageClient(abc.ABC):
    @abc.abstractmethod
    def upload(
        self, file_stream: io.BytesIO, filename: str, folder_id: Optional[str] = None
    ) -> str:
        pass

    @abc.abstractmethod
    def share(self, file_id: str, email: str, role: FileRole = FileRole.READER) -> None:
        pass

    @abc.abstractmethod
    def download(self, file_id: str) -> io.BytesIO:
        pass

    @abc.abstractmethod
    def get_file_url(self, file_id: str) -> str:
        pass


class GoogleDriveClient(StorageClient):
    def __init__(self, scopes=None):
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/drive"]
        self.scopes = scopes
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticate using a service account and return the Google Drive API service."""
        creds, _ = default(scopes=self.scopes)
        if creds is None:
            raise ValueError("No valid credentials found")
        return build("drive", "v3", credentials=creds)

    def upload(
        self,
        file_stream: bytes,
        filename: str,
        folder_id=None,
        custom_property=None,
    ):
        """Upload a file to Google Drive."""
        file_metadata = {"name": filename}
        if folder_id:
            file_metadata["parents"] = [folder_id]
        media = MediaIoBaseUpload(io.BytesIO(file_stream), mimetype="application/pdf")
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        file_id = file.get("id")
        if custom_property:
            self._set_custom_property(file_id, custom_property)
        return file_id

    def _set_custom_property(self, file_id: str, properties: Dict[str, str]):
        """Set custom properties for a file."""
        self.service.files().update(
            fileId=file_id,
            body={"properties": properties},
            fields="id,properties",
        ).execute()

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

    def _get_file_by_response_id(self, response_id: str):
        """Get a file ID by its response_id."""
        query = f"properties has {{ key='response_id' and value='{response_id}' }}"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])
        if files:
            return files[0]  # Return the first match
        return None

    def get_file_url(self, response_id):
        """Generate a sharable link for the file."""
        try:
            file_info = self._get_file_by_response_id(response_id)
            if not file_info:
                raise FileNotFoundError(f"File not found: {response_id}")

            file = (
                self.service.files()
                .get(fileId=file_info["id"], fields="webViewLink")
                .execute()
            )
            return file.get("webViewLink")
        except FileNotFoundError:
            return ""

    def download(self, response_id):
        """Download a file by its ID."""
        file_info = self._get_file_by_response_id(response_id)
        if not file_info:
            raise FileNotFoundError(f"File not found: {response_id}")

        request = self.service.files().get_media(fileId=file_info["id"])
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        file_stream.seek(0)
        return file_stream


class LocalStorageClient(StorageClient):
    DIRECTORY = "logs"

    def upload(self, file_stream, filename, folder_id=None, properties=None) -> str:
        with open(f"{self.DIRECTORY}/{filename}", "wb") as f:
            f.write(file_stream.read())
        return filename

    def share(self, file_id, email, role=FileRole.READER):
        pass

    def download(self, response_id):
        return open(f"{self.DIRECTORY}/{response_id}.pdf", "rb")

    def get_file_url(self, response_id):
        pass
