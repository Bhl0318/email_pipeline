from requests_toolbelt import MultipartEncoder
import requests
import json,os
from typing import Optional, Tuple


class PdfRestClient:
    def __init__(self,
                 api_key: Optional[str] = None,
                 endpoint_url: str = 'https://api.pdfrest.com/flattened-forms-pdf',
                 file_cache_dir: str = r'data/docs/file_cache') -> None:
        self.endpoint_url = endpoint_url
        self.api_key = api_key or os.environ.get('PDFREST_API_KEY') or '4b177438-f97c-4a4f-b0d1-ee91bea77b80'
        self.file_cache_dir = file_cache_dir

    def flatten_forms(self,
                      file_path: str,
                      output_name: str = 'example_out',
                      save_as: Optional[str] = None) -> Tuple[Optional[dict], Optional[str]]:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")

        original_name = os.path.basename(file_path)
        download_name = save_as or original_name

        with open(file_path, 'rb') as f:
            mp_encoder = MultipartEncoder(
                fields={
                    'file': (original_name, f, 'application/pdf'),
                    'output': output_name,
                }
            )

            headers = {
                'Accept': 'application/json',
                'Api-Key': self.api_key,
                'Content-Type': mp_encoder.content_type,
            }

            print("Sending POST request to flattened-forms-pdf endpoint...")
            response = requests.post(self.endpoint_url, data=mp_encoder, headers=headers)

        print("Response status code: " + str(response.status_code))

        if response.ok:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
        else:
            print(response.text)
            return None, None
        output_url = response_json.get("outputUrl") if isinstance(response_json, dict) else None
        if not output_url:
            print("响应中未找到 'outputUrl'")
            return response_json, None

        print(f"正在从以下地址下载文件: {output_url}")
        file_response = requests.get(output_url)
        if not file_response.ok:
            print(f"下载文件失败，状态码: {file_response.status_code}")
            print(file_response.text)
            return response_json, None

        output_dir = self.file_cache_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        saved_path = os.path.join(output_dir, download_name)
        with open(saved_path, "wb") as out_f:
            out_f.write(file_response.content)
        print(f"文件成功下载到: {saved_path}")

        return response_json, saved_path


if __name__ == '__main__':
    client = PdfRestClient()
    client.flatten_forms(file_path='path/to/input.pdf', output_name='example_out', save_as='output.pdf')
    print("PdfRestClient ready. Import and use PdfRestClient.flatten_forms(...) in your code.")
