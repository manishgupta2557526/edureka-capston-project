from io import BytesIO

from app.upload_service import UploadService


class _FastApiStyleUpload:
    def __init__(self, payload: bytes) -> None:
        self.file = BytesIO(payload)


def test_save_upload_supports_fastapi_uploadfile_shape(tmp_path):
    service = UploadService(storage_dir=str(tmp_path))
    uploaded = _FastApiStyleUpload(b"hello from fastapi")

    saved_path = service.save_upload(uploaded, "fastapi.txt")

    assert tmp_path.joinpath("fastapi.txt").read_bytes() == b"hello from fastapi"
    assert str(tmp_path.joinpath("fastapi.txt")) == saved_path


def test_save_upload_supports_streamlit_uploadedfile_shape(tmp_path):
    service = UploadService(storage_dir=str(tmp_path))
    uploaded = BytesIO(b"hello from streamlit")

    saved_path = service.save_upload(uploaded, "streamlit.txt")

    assert tmp_path.joinpath("streamlit.txt").read_bytes() == b"hello from streamlit"
    assert str(tmp_path.joinpath("streamlit.txt")) == saved_path