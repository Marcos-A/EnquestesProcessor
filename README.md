# INSTALL:
- pip
- macOS/Windows: GTK+ libraries

# RUN:
- Execució d'estadística:
    ```bash
    python EnquestesProcessor.py [<seetings_file.yaml>]
    ```
- Execució de tests complets:
    ```bash
    python EnquestesProcessor.py -t [verbosity: <0> | <1> | <2>]
    ```
- Execució de tests unitaris:
    ```bash
    python EnquestesProcessor.py -t -u [verbosity: <0> | <1> | <2>]
    ```
- Execució de test d'execució completa del codi:
    ```
    python EnquestesProcessor.py -t -c"
    ```

# IN CASE OF ERROR:
- ImportError: cannot import name '_imaging' from 'PIL' (/usr/lib/python3/dist-packages/PIL/__init__.py)
    ```bash
    pip install --upgrade --force-reinstall pillow
    ```
