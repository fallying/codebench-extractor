import os
import glob
import pandas as pd


class MergeCsvs:
    """Class Responsável por mergear os arquivos de csv gerados"""
    @staticmethod
    def merge():
        os.chdir("./csv")

        file_extension = '.csv'
        all_filenames = [i for i in glob.glob(f"*{file_extension}")]

        combined_csv_data = pd.concat([pd.read_csv(path, sep=',', encoding='utf-8', quoting=2) for path in all_filenames])

        os.chdir('../mergecvs')

        combined_csv_data.to_csv('combined_csv_data.csv')
