import pandas as pd

def find_best_result(csv_file, output_file="best_result.csv"):
    """
    Load results from a CSV file, find the best result, and save it to a file.

    Args:
        csv_file (str): Path to the CSV file containing results.
        output_file (str): Path to save the best result (default: "best_result.csv").

    Returns:
        dict: The best result as a dictionary.
    """
    try:
        # Load the results from the CSV file
        results_df = pd.read_csv(csv_file)

        # Drop rows with missing or non-numeric objective values
        results_df["objective_value"] = pd.to_numeric(results_df["objective_value"], errors="coerce")
        results_df = results_df.dropna(subset=["objective_value"])

        # Convert objective_value to numeric (if required)
        results_df["objective_value"] = results_df["objective_value"].astype(float)

        # Find the row with the highest objective_value
        best_result = results_df.loc[results_df["objective_value"].idxmax()]

        # Save the best result to a new CSV file
        best_result.to_frame().T.to_csv(output_file, index=False)

        print(f"Best result saved to {output_file}")
        return best_result.to_dict()

    except Exception as e:
        print(f"Error processing the file: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Replace 'results.csv' with your CSV file containing the results
    csv_file = "hyperparameter_tuning_results.csv"
    best_result = find_best_result(csv_file)

    if best_result:
        print("Best Configuration:")
        print(best_result)
