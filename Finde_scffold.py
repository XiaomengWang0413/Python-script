import os
import pandas as pd
import argparse

def find_keyword_in_tsv(folder_path, keyword):
    """
    Search for a keyword in all TSV files within a folder
    
    Parameters:
    folder_path (str): Path to the folder containing TSV files
    keyword (str): Keyword to search for
    """
    found_files = []
    
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.tsv'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                # Try different encodings to handle various file formats
                for encoding in ['utf-8', 'latin1', 'ISO-8859-1']:
                    try:
                        # Read file in chunks for memory efficiency
                        chunks = pd.read_csv(file_path, sep='\t', chunksize=10000, 
                                            dtype=str, encoding=encoding)
                        found = False
                        
                        for chunk in chunks:
                            # Convert all columns to string and search for keyword
                            for col in chunk.columns:
                                # Check if any row in the column contains the keyword
                                if any(chunk[col].astype(str).str.contains(keyword, case=False, na=False)):
                                    found_files.append(filename)
                                    found = True
                                    break
                            if found:
                                break
                        if found:
                            break
                    
                    except UnicodeDecodeError:
                        continue  # Try next encoding if this one fails
                
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
    
    # Display results
    if found_files:
        print(f"\nKeyword '{keyword}' found in the following files:")
        for file in found_files:
            print(f"- {file}")
    else:
        print(f"\nKeyword '{keyword}' not found in any files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search for a keyword in TSV files')
    parser.add_argument('folder', help='Folder containing TSV files')
    parser.add_argument('keyword', help='Keyword to search for')
    
    args = parser.parse_args()
    
    find_keyword_in_tsv(args.folder, args.keyword)
