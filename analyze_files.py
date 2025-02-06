import pandas as pd
from difflib import SequenceMatcher

def analyze_files(ventas_file, guias_file, output_file, months):
    """
    Analyze files for the specified months and generate an output Excel file.

    Parameters:
        ventas_file (str): Path to the Ventas_Live_Actualizado file.
        guias_file (str): Path to the BusquedaGuias file.
        output_file (str): Path to save the output Excel file.
        months (list): List of months (in 'YYYY-MM' format) to analyze.
    """
    # Load the "Ventas_Live_Actualizado" Excel file
    ventas_live_data = pd.ExcelFile(ventas_file)
    ventas_live_df = pd.read_excel(ventas_file, sheet_name=ventas_live_data.sheet_names[0])

    # Load the "BusquedaGuias" Excel file
    guias_data = pd.ExcelFile(guias_file)
    guias_df = pd.read_excel(guias_file, sheet_name=guias_data.sheet_names[0])

    # Prepare the "BusquedaGuias" dataset for analysis
    guias_df['Destinatario'] = guias_df['Destinatario'].astype(str).str.strip().str.lower()

    # Ensure 'Fecha' in ventas is in datetime format
    ventas_live_df['Fecha'] = pd.to_datetime(ventas_live_df['Fecha'], errors='coerce')

    # Initialize a list to collect all results
    all_results = []

    for month in months:
        # Filter the ventas data for the specified month
        ventas_month = ventas_live_df[ventas_live_df['Fecha'].dt.to_period('M') == month]
        ventas_month['Cliente'] = ventas_month['Cliente'].astype(str).str.strip().str.lower()

        # Perform similarity matching for the month
        for _, row in ventas_month.iterrows():
            client = row['Cliente']
            best_match = None
            best_similarity = 0
            best_row = None

            for _, guia_row in guias_df.iterrows():
                destinatario = guia_row['Destinatario']
                similarity = SequenceMatcher(None, client, destinatario).ratio()

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = destinatario
                    best_row = guia_row

            if best_similarity >= 0.6:  # Threshold of 60%
                all_results.append({
                    'Mes': month,
                    'Fecha Venta': row['Fecha'],
                    'Cliente': row['Cliente'],
                    'Envio': row['Envio'],
                    'Destinatario Más Similar': best_match,
                    'Similitud': best_similarity,
                    'Fecha Guia': best_row['Fecha'] if best_row is not None else None,
                    'Referencia 1': best_row['Referencia 1'] if best_row is not None else None,
                    'Referencia 2': best_row['Referencia 2'] if best_row is not None else None,
                    'Estado': best_row['Estado'] if best_row is not None else None
                })
            else:
                all_results.append({
                    'Mes': month,
                    'Fecha Venta': row['Fecha'],
                    'Cliente': row['Cliente'],
                    'Envio': row['Envio'],
                    'Destinatario Más Similar': None,
                    'Similitud': None,
                    'Fecha Guia': None,
                    'Referencia 1': None,
                    'Referencia 2': None,
                    'Estado': None
                })

    # Convert all results into a DataFrame and save to Excel
    all_results_df = pd.DataFrame(all_results)
    all_results_df.to_excel(output_file, index=False)

# Example usage
analyze_files('Ventas_Live_Actualizado.xlsx', 'BusquedaGuias (80).xlsx', 'Comparacion_Varios_Meses.xlsx', ['2024-12'])
