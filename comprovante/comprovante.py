def gerar_comprovante(venda_id, data_hora, itens, total, forma_pagamento, loja):
    largura = 40
    linhas = []

    linhas.append("=" * largura)
    linhas.append(loja["nome"].center(largura))
    if loja.get("slogan"):
        linhas.append(loja["slogan"].center(largura))
    if loja.get("endereco"):
        linhas.append(loja["endereco"].center(largura))
    if loja.get("telefone"):
        linhas.append(f'Tel: {loja["telefone"]}'.center(largura))
    if loja.get("cnpj"):
        linhas.append(f'CNPJ: {loja["cnpj"]}'.center(largura))
    linhas.append("=" * largura)
    linhas.append(f"Venda #: {str(venda_id).ljust(largura - 9)}")
    linhas.append(f"Data:    {data_hora}")
    linhas.append("-" * largura)
    linhas.append("Item           Qtd    V.Un     Sub")
    linhas.append("-" * largura)

    for item in itens:
        nome = item["nome_produto"][:14].ljust(14)
        qtd = str(item["quantidade"]).center(5)
        preco = f'{item["preco_unitario"]:.2f}'.center(7)
        subtotal = f'{item["quantidade"] * item["preco_unitario"]:.2f}'.rjust(7)
        linhas.append(f"{nome} {qtd} {preco} {subtotal}")

    linhas.append("-" * largura)
    linhas.append(f"TOTAL:".ljust(largura - 12) + f"R$ {total:>8.2f}")
    linhas.append(f"PAGAMENTO: {forma_pagamento.upper()}")
    linhas.append("=" * largura)
    linhas.append("Obrigado pela preferência!".center(largura))
    linhas.append(f"Desenvolvido por Core Tech".center(largura))
    linhas.append("=" * largura)

    return "\n".join(linhas)
