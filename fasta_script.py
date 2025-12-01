import csv
import sys
import os

def create_fasta_from_csv(csv_filepath, output_filepath, target_ids, extract_all_flag=False):
    """
    Extracts sequence data from a CSV file. If extract_all_flag is True,
    all valid sequences are extracted. Otherwise, only sequences matching 
    the IDs in target_ids are extracted.

    Args:
        csv_filepath (str): Path to the input CSV file.
        output_filepath (str): Path to the output FASTA file.
        target_ids (set): Set of SEQ_IDs (strings) to filter and extract. 
                          Only used if extract_all_flag is False.
        extract_all_flag (bool): If True, extract all sequences regardless of target_ids.
    """
    # Define the expected column names based on your database structure
    ID_COLUMN = 'SEQ_ID'
    NAME_COLUMN = 'SHORT_NAME'
    SEQUENCE_COLUMN = 'PROTEIN_SEQUENCE'
    
    extracted_count = 0
    
    # Determine what message to print based on the extraction mode
    if extract_all_flag:
        start_message = "Starting extraction of ALL sequences..."
    else:
        start_message = f"Starting extraction for {len(target_ids)} target ID(s)..."

    try:
        # 1. Open and read the CSV file using DictReader for header access
        with open(csv_filepath, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Check if all required headers are present
            required_headers = [ID_COLUMN, NAME_COLUMN, SEQUENCE_COLUMN]
            if not all(header in reader.fieldnames for header in required_headers):
                print(f"\nError: CSV file is missing one or more required headers.")
                print(f"Expected headers: {required_headers}")
                print(f"Found headers: {reader.fieldnames}")
                return

            # 2. Open the output file for writing the FASTA entries
            with open(output_filepath, mode='w', encoding='utf-8') as outfile:
                print(start_message)
                
                # 3. Iterate over each row in the CSV
                for row in reader:
                    seq_id = row.get(ID_COLUMN)
                    
                    # 4. FILTERING LOGIC: Extract if 'all' is requested OR if the specific ID is in the target set
                    is_match = extract_all_flag or (seq_id and seq_id in target_ids)
                    
                    if is_match:
                        # Data extraction
                        short_name = row.get(NAME_COLUMN, 'N/A')
                        protein_sequence = row.get(SEQUENCE_COLUMN, '').strip()

                        # The FASTA name is the combined construct name: SEQ_ID_SHORT_NAME
                        fasta_name = f"{seq_id}_{short_name}"
                        
                        # Format and write the FASTA entry (only if a sequence exists)
                        if protein_sequence:
                            # FASTA header must start with '>'
                            outfile.write(f">{fasta_name}\n")
                            
                            # Write sequence, wrapping lines at 60 characters (standard FASTA format)
                            for i in range(0, len(protein_sequence), 60):
                                outfile.write(protein_sequence[i:i+60] + '\n')
                                
                            extracted_count += 1
                        else:
                            warning_id = seq_id if seq_id else 'Unknown ID'

            print("-" * 40)
            print(f"Process complete. Extracted {extracted_count} sequence(s) to '{output_filepath}'")
            print("-" * 40)

    except FileNotFoundError:
        print(f"\nError: The input file '{csv_filepath}' was not found. Please verify the path and file name.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)


# --- User Configuration Section (Script Entry Point) ---

if __name__ == "__main__":
    
    # --- 1. Get File Paths from User Input ---
    print("\n--- FASTA Converter Setup ---")
    INPUT_CSV_FILE = input("Enter your input CSV filepath (e.g., C:\\data\\database.csv): ").strip()
    OUTPUT_FASTA_FILE = input("Enter your desired output FASTA filepath (e.g., output.fasta): ").strip()

    # --- 2. Get Target IDs/Mode from User Input ---
    id_input = input("Which IDs would you like to extract? (Use commas to separate multiple, or type 'all'): ").strip()
    
    # Check for the 'all' command (case-insensitive)
    EXTRACT_ALL = id_input.lower() == "all"
    
    TARGET_IDS_SET = set()
    
    if not EXTRACT_ALL:
        # Process the input string: split by comma, strip spaces, and filter out empty strings
        TARGET_IDS_LIST = [id.strip() for id in id_input.split(',') if id.strip()]
        
        # Convert the list to a set for highly efficient lookup
        TARGET_IDS_SET = set(TARGET_IDS_LIST)

    # --- 3. Run the extraction based on the mode ---
    
    if not EXTRACT_ALL and not TARGET_IDS_SET:
        print("\nOperation cancelled: No valid SEQ_IDs were entered, and 'all' was not specified.")
    elif not os.path.exists(INPUT_CSV_FILE):
        print(f"\nError: The input CSV file '{INPUT_CSV_FILE}' was not found. Please check the filepath.")
    else:
        # Call the main function with all necessary parameters
        create_fasta_from_csv(
            INPUT_CSV_FILE, 
            OUTPUT_FASTA_FILE, 
            TARGET_IDS_SET, 
            EXTRACT_ALL
        )
