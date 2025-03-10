"""Integration agent for connecting with external services in the Tío Pepe system."""

from typing import Dict, Any
import logging
import json
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class IntegrationAgent:
    """Specialized agent for handling external service integrations."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.credentials = {}
        self.clients = {}
        self.credentials_path = 'config/credentials/'
        self._initialize_services()

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process an integration task based on its type."""
        service_type = task.get('service_type')
        action_type = task.get('action_type')
        
        if not service_type or not action_type:
            raise ValueError("Service type and action type must be provided")

        try:
            if service_type == 'google_drive':
                return self._handle_google_drive(action_type, task)
            elif service_type == 'slack':
                return self._handle_slack(action_type, task)
            else:
                raise ValueError(f"Unsupported service type: {service_type}")

        except Exception as e:
            self.logger.error(f"Integration task error: {str(e)}")
            raise

    def _initialize_services(self) -> None:
        """Initialize connections to external services."""
        try:
            self._setup_google_drive()
            self._setup_slack()
        except Exception as e:
            self.logger.error(f"Service initialization error: {str(e)}")

    def _setup_google_drive(self) -> None:
        """Setup Google Drive API client."""
        try:
            creds = None
            token_path = os.path.join(self.credentials_path, 'google_token.json')
            credentials_path = os.path.join(self.credentials_path, 'google_credentials.json')

            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, ['https://www.googleapis.com/auth/drive'])
                    creds = flow.run_local_server(port=0)

                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            self.clients['google_drive'] = build('drive', 'v3', credentials=creds)
            self.logger.info("Google Drive client initialized successfully")

        except Exception as e:
            self.logger.error(f"Google Drive setup error: {str(e)}")
            raise

    def _setup_slack(self) -> None:
        """Setup Slack API client."""
        try:
            slack_token_path = os.path.join(self.credentials_path, 'slack_token.txt')
            if os.path.exists(slack_token_path):
                with open(slack_token_path, 'r') as f:
                    slack_token = f.read().strip()
                self.clients['slack'] = WebClient(token=slack_token)
                self.logger.info("Slack client initialized successfully")
            else:
                self.logger.warning("Slack token not found")

        except Exception as e:
            self.logger.error(f"Slack setup error: {str(e)}")
            raise

    def _handle_google_drive(self, action_type: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Google Drive related tasks."""
        if 'google_drive' not in self.clients:
            raise ValueError("Google Drive client not initialized")

        drive_service = self.clients['google_drive']

        if action_type == 'upload':
            return self._upload_to_drive(drive_service, task)
        elif action_type == 'download':
            return self._download_from_drive(drive_service, task)
        elif action_type == 'list':
            return self._list_drive_files(drive_service, task)
        else:
            raise ValueError(f"Unsupported Google Drive action: {action_type}")

    def _handle_slack(self, action_type: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack related tasks."""
        if 'slack' not in self.clients:
            raise ValueError("Slack client not initialized")

        slack_client = self.clients['slack']

        if action_type == 'send_message':
            return self._send_slack_message(slack_client, task)
        elif action_type == 'get_messages':
            return self._get_slack_messages(slack_client, task)
        else:
            raise ValueError(f"Unsupported Slack action: {action_type}")

    def _upload_to_drive(self, service, task: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a file to Google Drive."""
        try:
            file_path = task.get('file_path')
            file_name = task.get('file_name')
            mime_type = task.get('mime_type', 'application/octet-stream')

            if not file_path or not file_name:
                raise ValueError("File path and name must be provided")

            file_metadata = {'name': file_name}
            media = service.files().create(
                body=file_metadata,
                media_body=file_path,
                fields='id'
            ).execute()

            return {
                'file_id': media.get('id'),
                'status': 'success',
                'message': f"File {file_name} uploaded successfully"
            }

        except Exception as e:
            self.logger.error(f"Upload to Drive error: {str(e)}")
            raise

    def _download_from_drive(self, service, task: Dict[str, Any]) -> Dict[str, Any]:
        """Download a file from Google Drive."""
        try:
            file_id = task.get('file_id')
            download_path = task.get('download_path')

            if not file_id or not download_path:
                raise ValueError("File ID and download path must be provided")

            request = service.files().get_media(fileId=file_id)
            with open(download_path, 'wb') as f:
                f.write(request.execute())

            return {
                'status': 'success',
                'message': f"File downloaded successfully to {download_path}"
            }

        except Exception as e:
            self.logger.error(f"Download from Drive error: {str(e)}")
            raise

    def _list_drive_files(self, service, task: Dict[str, Any]) -> Dict[str, Any]:
        """List files in Google Drive."""
        try:
            query = task.get('query', "")
            page_size = task.get('page_size', 10)

            results = service.files().list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, createdTime)",
                q=query
            ).execute()

            return {
                'files': results.get('files', []),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"List Drive files error: {str(e)}")
            raise

    def _send_slack_message(self, client, task: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to a Slack channel."""
        try:
            channel = task.get('channel')
            message = task.get('message')

            if not channel or not message:
                raise ValueError("Channel and message must be provided")

            response = client.chat_postMessage(
                channel=channel,
                text=message
            )

            return {
                'status': 'success',
                'message_ts': response['ts'],
                'channel': response['channel']
            }

        except SlackApiError as e:
            self.logger.error(f"Slack API error: {str(e)}")
            raise

    def _get_slack_messages(self, client, task: Dict[str, Any]) -> Dict[str, Any]:
        """Get messages from a Slack channel."""
        try:
            channel = task.get('channel')
            limit = task.get('limit', 100)

            if not channel:
                raise ValueError("Channel must be provided")

            response = client.conversations_history(
                channel=channel,
                limit=limit
            )

            return {
                'messages': response['messages'],
                'status': 'success',
                'has_more': response['has_more']
            }

        except SlackApiError as e:
            self.logger.error(f"Slack API error: {str(e)}")
            raise