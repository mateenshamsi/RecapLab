import boto3
import uuid
import os
from datetime import datetime, timedelta
from typing import Optional, BinaryIO
from botocore.exceptions import ClientError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class S3StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.bucket_prefix = settings.S3_BUCKET_PREFIX

    def generate_file_key(self, job_id: str, file_type: str, extension: str) -> str:
        """Generate S3 key for file storage"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        return f"{self.bucket_prefix}/{timestamp}/{job_id}/{file_type}.{extension}"

    async def upload_audio_file(self, file: BinaryIO, filename: str, job_id: str) -> tuple[str, str]:
        """
        Upload audio file to S3
        Returns: (s3_key, s3_url)
        """
        try:
            # Extract file extension
            file_extension = filename.split('.')[-1].lower()
            
            # Generate S3 key
            s3_key = self.generate_file_key(job_id, "audio", file_extension)
            
            # Upload file to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': f'audio/{file_extension}',
                    'Metadata': {
                        'job_id': job_id,
                        'original_filename': filename,
                        'upload_timestamp': datetime.utcnow().isoformat()
                    }
                }
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            
            logger.info(f"Successfully uploaded audio file for job {job_id} to S3: {s3_key}")
            return s3_key, s3_url
            
        except ClientError as e:
            logger.error(f"Failed to upload audio file for job {job_id}: {str(e)}")
            raise Exception(f"S3 upload failed: {str(e)}")

    async def save_text_file(self, content: str, job_id: str, file_type: str) -> tuple[str, str]:
        """
        Save text content (transcript, summary, etc.) to S3
        Returns: (s3_key, s3_url)
        """
        try:
            s3_key = self.generate_file_key(job_id, file_type, "txt")
            
            # Upload text content to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content.encode('utf-8'),
                ContentType='text/plain',
                Metadata={
                    'job_id': job_id,
                    'file_type': file_type,
                    'created_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            s3_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            
            logger.info(f"Successfully saved {file_type} for job {job_id} to S3: {s3_key}")
            return s3_key, s3_url
            
        except ClientError as e:
            logger.error(f"Failed to save {file_type} for job {job_id}: {str(e)}")
            raise Exception(f"S3 save failed: {str(e)}")

    async def get_file_content(self, s3_key: str) -> str:
        """Retrieve text file content from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            logger.error(f"Failed to retrieve file {s3_key}: {str(e)}")
            raise Exception(f"S3 retrieval failed: {str(e)}")

    async def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file download"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {s3_key}: {str(e)}")
            raise Exception(f"Presigned URL generation failed: {str(e)}")

    async def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Successfully deleted file from S3: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file {s3_key}: {str(e)}")
            return False

# Create storage service instance
storage_service = S3StorageService()