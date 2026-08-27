"""Smoke test: prova que o pacote instalado (editable) importa de ponta a ponta."""


def test_import_package() -> None:
    import tutor_rag

    assert tutor_rag.__name__ == "tutor_rag"
