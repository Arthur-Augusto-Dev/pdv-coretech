import os
import sys


def imprimir_comprovante(texto_cupom):
    """
    Tenta imprimir na impressora térmica.
    Se não houver impressora configurada, salva em arquivo.
    """
    try:
        import win32print

        printer_name = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            print_job = win32print.StartDocPrinter(
                hPrinter, 1, ("Cupom PDV", None, "RAW")
            )
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, texto_cupom.encode("utf-8"))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            return True, "Impresso com sucesso!"
        finally:
            win32print.ClosePrinter(hPrinter)
    except ImportError:
        # win32print não disponível — salva em arquivo
        return salvar_comprovante_arquivo(texto_cupom)
    except Exception as e:
        # Impressora com erro — salva em arquivo
        return salvar_comprovante_arquivo(texto_cupom)


def salvar_comprovante_arquivo(texto_cupom):
    """
    Salva o comprovante em arquivo .txt como fallback.
    """
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta = os.path.join(BASE_DIR, "comprovantes")
        os.makedirs(pasta, exist_ok=True)

        from datetime import datetime

        nome_arquivo = datetime.now().strftime("cupom_%Y%m%d_%H%M%S.txt")
        caminho = os.path.join(pasta, nome_arquivo)

        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto_cupom)

        return True, f"Comprovante salvo em: {caminho}"
    except Exception as e:
        return False, f"Erro ao salvar comprovante: {str(e)}"
