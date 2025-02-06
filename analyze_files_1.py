import pandas as pd
from difflib import SequenceMatcher

def analyze_files(envios_file, guias_file, output_file, sheet_name):
    """
    Analyze files for the specified sheet and generate an output Excel file.

    Parameters:
        envios_file (str): Path to the Ventas almacen Gaby file.
        guias_file (str): Path to the BusquedaGuias file.
        output_file (str): Path to save the output Excel file.
        sheet_name (str): Sheet name to analyze in the envios file.
    """
    # Load the "Ventas almacen Gaby" Excel file
    envios_data = pd.read_excel(envios_file, sheet_name=sheet_name)

    # Load the "BusquedaGuias" Excel file
    guias_data = pd.read_excel(guias_file)

    # Prepare the "BusquedaGuias" dataset for analysis
    guias_data['Destinatario'] = guias_data['Destinatario'].astype(str).str.strip().str.lower()

    # Add a new column based on the conditions for "CO" and "Recargo 4%"
    def classify_envio(row):
        if pd.notna(row['CO']) and row['CO'] == 'F':
            return 'Forza'
        elif pd.isna(row['CO']) and (pd.isna(row['Recargo 4%']) or row['Recargo 4%'] == 0):
            return 'Mensajero'
        elif pd.isna(row['CO']) and row['Recargo 4%'] > 0:
            return 'Cargo'
        else:
            return 'Unknown'

    envios_data['Clasificación'] = envios_data.apply(classify_envio, axis=1)

    # Perform similarity matching by "Nombre Envio" with the "Busqueda Guias" file
    all_results = []
    for _, row in envios_data.iterrows():
        nombre_envio = str(row['Nombre Envio']).strip().lower()
        best_match = None
        best_similarity = 0
        best_row = None

        for _, guia_row in guias_data.iterrows():
            destinatario = guia_row['Destinatario']
            similarity = SequenceMatcher(None, nombre_envio, destinatario).ratio()

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = destinatario
                best_row = guia_row

        if best_similarity >= 0.6:  # Threshold of 60%
            all_results.append({
                'Fecha': row['Fecha'],
                'Nombre Envio': row['Nombre Envio'],
                'Clasificación': row['Clasificación'],
                'Destinatario Más Similar': best_match,
                'Similitud': best_similarity,
                'Referencia 1': best_row['Referencia 1'] if best_row is not None else None,
                'Referencia 2': best_row['Referencia 2'] if best_row is not None else None,
                'Estado': best_row['Estado'] if best_row is not None else None,
                'Fecha envio': best_row['Fecha'] if best_row is not None else None,
            })
        else:
            all_results.append({
                'Fecha': row['Fecha'],
                'Nombre Envio': row['Nombre Envio'],
                'Clasificación': row['Clasificación'],
                'Destinatario Más Similar': None,
                'Similitud': None,
                'Referencia 1': None,
                'Referencia 2': None,
                'Estado': None,
                'Fecha envio': None
            })

    # Convert all results into a DataFrame
    comparison_result_df = pd.DataFrame(all_results)

    # Save the results to an Excel file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        envios_data.to_excel(writer, sheet_name='Clasificación Envios', index=False)
        comparison_result_df.to_excel(writer, sheet_name='Comparación', index=False)

# Ejemplo de uso
analyze_files('Ventas almacen Gaby  - 2024  ULTIMATE.xlsx', 'BusquedaGuias (83).xlsx', 'Reporte_Envios_Dic2024Comparacion.xlsx', 'Diciembre')
