import os
from pathlib import Path
import convertapi
import requests

CONVERTAPI_CREDENTIALS = os.getenv("CONVERTAPI_CREDENTIALS")
PDFENDPOINT_API_KEY = os.getenv("PDFENDPOINT_API_KEY")

def convert_md_to_html(md_file_path, output_filename=None, api_credentials=None):
    """
    Convert Markdown file to HTML using ConvertAPI.

    Args:
        md_file_path (str): Path to the Markdown file
        output_filename (str, optional): Output filename without extension
        api_credentials (str, optional): ConvertAPI credentials

    Returns:
        str: Path to the created HTML file if successful, None otherwise
    """
    try:
        # Set API credentials
        if api_credentials:
            convertapi.api_credentials = api_credentials
        else:
            convertapi.api_credentials = CONVERTAPI_CREDENTIALS

        # Generate output filename if not provided
        if output_filename is None:
            md_path = Path(md_file_path)
            output_filename = md_path.stem

        # Determine output directory
        md_path = Path(md_file_path)
        output_dir = md_path.parent
        output_html_path = output_dir / f"{output_filename}.html"

        # Convert MD to HTML
        convertapi.convert('html', {
            'File': md_file_path
        }, from_format='md').save_files(str(output_html_path))

        print(f"✅ Arquivo HTML criado com sucesso: {output_html_path}")
        return str(output_html_path)

    except Exception as e:
        print(f"❌ Erro ao converter MD para HTML: {str(e)}")
        return None

def convert_html_to_pdf(html_file_path, output_pdf_path=None, css_file_path=None, api_key=None):
    """
    Convert HTML file to PDF using PDFEndpoint API.

    Args:
        html_file_path (str): Path to the HTML file
        output_pdf_path (str, optional): Path for the output PDF file
        css_file_path (str, optional): Path to CSS file for styling
        api_key (str, optional): PDFEndpoint API key

    Returns:
        str: Path to the created PDF file if successful, None otherwise
    """
    try:
        # Set default output path if not provided
        if output_pdf_path is None:
            html_path = Path(html_file_path)
            output_pdf_path = html_path.with_suffix('.pdf')

        # Set API key
        if api_key is None:
            api_key = PDFENDPOINT_API_KEY

        # Read HTML content
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Read CSS content if provided
        css_content = ""
        if css_file_path and os.path.exists(css_file_path):
            with open(css_file_path, "r", encoding="utf-8") as f:
                css_content = f.read()

        # Prepare API request
        url = "https://api.pdfendpoint.com/v1/convert"
        payload = {
            "html": html_content,
            "sandbox": True,
            "orientation": "vertical",
            "page_size": "A4",
            "no_backgrounds": True,
            "css": css_content
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Make API request
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status da resposta da API: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()

            if response_data.get('success') and 'data' in response_data:
                pdf_url = response_data['data']['url']
                page_count = response_data['data']['page_count']
                file_size = response_data['data']['file_size']

                print(f"✅ Geração de PDF bem-sucedida!")
                print(f"📄 Páginas: {page_count}")
                print(f"📏 Tamanho do arquivo: {file_size:,} bytes")

                # Download the PDF file
                pdf_response = requests.get(pdf_url)

                if pdf_response.status_code == 200:
                    with open(output_pdf_path, "wb") as f:
                        f.write(pdf_response.content)
                    print(f"✅ Arquivo PDF salvo com sucesso: {output_pdf_path}")
                    return str(output_pdf_path)
                else:
                    print(f"❌ Erro ao baixar PDF: {pdf_response.status_code}")
                    return None
            else:
                print("❌ Resposta da API indica falha")
                print(f"Resposta: {response.text}")
                return None

        else:
            print(f"❌ Erro ao criar PDF: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro ao converter HTML para PDF: {str(e)}")
        return None

def convert_md_to_pdf(md_file_path, output_pdf_path=None, css_file_path=None,
                      convertapi_credentials=None, pdfendpoint_api_key=None):
    """
    Complete pipeline: Convert Markdown to HTML and then to PDF.

    Args:
        md_file_path (str): Path to the Markdown file
        output_pdf_path (str, optional): Path for the output PDF file
        css_file_path (str, optional): Path to CSS file for styling
        convertapi_credentials (str, optional): ConvertAPI credentials
        pdfendpoint_api_key (str, optional): PDFEndpoint API key

    Returns:
        str: Path to the created PDF file if successful, None otherwise
    """
    try:
        # Step 1: Convert MD to HTML
        md_path = Path(md_file_path)
        temp_html_filename = f"temp_{md_path.stem}"

        html_file_path = convert_md_to_html(
            md_file_path,
            temp_html_filename,
            convertapi_credentials
        )

        if not html_file_path:
            return None

        # Step 3: Convert HTML to PDF
        if output_pdf_path is None:
            output_pdf_path = md_path.with_suffix('.pdf')

        pdf_file_path = convert_html_to_pdf(
            html_file_path,
            output_pdf_path,
            css_file_path,
            pdfendpoint_api_key
        )

        # Clean up temporary HTML file
        try:
            if os.path.exists(html_file_path):
                os.remove(html_file_path)
                print(f"🧹 Arquivo temporário removido: {html_file_path}")
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível remover o arquivo temporário {html_file_path}: {e}")

        return pdf_file_path

    except Exception as e:
        print(f"❌ Erro no pipeline de conversão MD para PDF: {str(e)}")
        return None

# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of the module functions.
    This section will only run when the script is executed directly.
    """
    print("=== Teste do Módulo Conversor de eBook ===")

    # Example 1: Convert existing MD file to PDF
    md_file = 'eBooks/IA Renda automática.md'
    css_file = 'ebook_style.css'

    if os.path.exists(md_file):
        print(f"\n🔄 Convertendo {md_file} para PDF...")
        pdf_path = convert_md_to_pdf(md_file, css_file_path=css_file)
        if pdf_path:
            print(f"✅ Sucesso! PDF criado em: {pdf_path}")
        else:
            print("❌ Falha ao criar PDF")
    else:
        print(f"❌ Arquivo de teste não encontrado: {md_file}")

        # Demonstrate the individual functions
        print("\n📚 Funções disponíveis neste módulo:")
        print("- apply_external_css_to_html()")
        print("- convert_html_to_external_css()")
        print("- convert_md_to_html()")
        print("- convert_html_to_pdf()")
        print("- convert_md_to_pdf()")
        print("\nPara usar essas funções, importe este módulo em seu script principal:")
        print("from ebook_converter import convert_md_to_pdf, convert_md_to_html")
