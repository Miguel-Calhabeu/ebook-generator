# main.py
import os
from ebook_tools.ebook_generator import generate_ebook_chapter, generate_ebook_outline, generate_ebook_introduction
from ebook_tools.ebook_converter import convert_md_to_pdf

def main():
    """
    Main function to run the eBook generation CLI.
    It prompts the user for the initial idea, target audience, and tone,
    then generates the eBook outline, introduction, and chapters,
    finally compiling them into Markdown and PDF files.
    """
    # Print a header to give the script a CLI feel
    print("===================================")
    print("    🚀 GERADOR DE EBOOK IA 🚀")
    print("===================================")
    print("\nPor favor, forneça as informações abaixo para começar.\n")

    #Get user input for the eBook
    ebook_title =  input("Título do eBook: ")
    ideia_inicial = input("Ideia inicial do eBook: ")
    publico_alvo = input("Público-alvo do eBook: ")
    tom_estilo = input("Tom e estilo do eBook: ")

    ebook_title = ebook_title.replace(" ", "_")

    print("\n🔄 Gerando outline do eBook...")
    ebook_outline = generate_ebook_outline(ideia_inicial, publico_alvo, tom_estilo)

    print("✍️  Escrevendo a introdução...")
    ebook_introduction = generate_ebook_introduction(ebook_outline)

    ebook_chapters = []
    total_chapters = len(ebook_outline.get("estrutura_capitulos", []))

    # Loop through each chapter in the outline and generate its content
    for i, chapter in enumerate(ebook_outline.get("estrutura_capitulos", [])):
        print(f"📖 Escrevendo Capítulo {chapter['capitulo']} de {total_chapters}...")
        ebook_chapter = generate_ebook_chapter(ebook_outline, chapter["capitulo"])
        ebook_chapters.append(ebook_chapter)

    print("\n⚙️  Montando o arquivo final...")
    # Combine the introduction and chapters into a single string
    ebook_content = f"""{ebook_introduction}\n\n{'\n\n'.join(ebook_chapters)}"""

    # Write the complete eBook to a Markdown file
    with open(f"dist/{ebook_title}.md", "w", encoding="utf-8") as f:
        f.write(ebook_content)
    print(f"✅ Arquivo {ebook_title}.md salvo com sucesso! em dist/")

    # Convert the Markdown file to PDF
    print("📄 Convertendo para PDF...")
    css_file_path = "ebook_style.css" if os.path.exists("ebook_style.css") else None
    pdf_path = convert_md_to_pdf(f"dist/{ebook_title}.md", f"dist/{ebook_title}.pdf", css_file_path)

    if pdf_path:
        print(f"✅ Arquivo PDF salvo com sucesso: {pdf_path}")
    else:
        print("❌ Erro ao converter para PDF")
    print("\n🎉 Processo concluído! Seu eBook está pronto.")


if __name__ == "__main__":
    main()
