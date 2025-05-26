import os
import numpy as np
import Levenshtein
from pyxdameraulevenshtein import damerau_levenshtein_distance 
import matplotlib.pyplot as plt
from python_ocr.models.inference import infer_page

class TestModel:
    def __init__(self, labels_txt, images_folder):
        self.labels_txt = labels_txt
        self.images_folder = images_folder
        self.real_labels = self.get_real_labels()

        self.metrics = {
            'jaro_distances': [],
            'character_error_rates_osa': [],
            'word_error_rates': [],
            'total_evaluated': 0
        }

    def get_real_labels(self):
        real_labels = {}
        with open(self.labels_txt, "r", encoding="utf-8") as f:
            for line in f:
                if " - " in line:
                    filename, text = line.strip().split(" - ", 1)
                    real_labels[filename.strip()] = text.strip()
        return real_labels

    def get_images(self):
        return [f for f in os.listdir(self.images_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    def calculate_jaro_distance(self, reference, prediction):
        return Levenshtein.jaro(reference, prediction)
    
    def calculate_cer_osa(self, reference, prediction):
        if len(reference) == 0:
            return 0 if len(prediction) == 0 else 1
        cer_osa = damerau_levenshtein_distance(reference, prediction)
        return min(cer_osa / len(reference), 1.0)
    
    def calculate_wer(self, reference, prediction):
        ref_words = reference.split()
        pred_words = prediction.split()
        if len(ref_words) == 0:
            return 0 if len(pred_words) == 0 else 1
        dist = damerau_levenshtein_distance(ref_words, pred_words)
        wer = dist / len(ref_words)
        return min(wer, 1.0)

    def test_predictions(self):
        all_images = self.get_images()
        real_labels = self.real_labels

        for image in sorted(all_images):
            image_path = os.path.join(self.images_folder, image)
            prediction = infer_page(image_path, dbg=False)

            print(f"Processing: {image}")
            print(f"Predicted Text: {prediction}")

            if image in real_labels:
                reference = real_labels[image]
                print("Expected Text:", reference)

                jaro_distance = self.calculate_jaro_distance(reference, prediction)
                cer_osa = self.calculate_cer_osa(reference, prediction)
                wer = self.calculate_wer(reference, prediction)

                self.metrics['jaro_distances'].append(jaro_distance)
                self.metrics['character_error_rates_osa'].append(cer_osa)
                self.metrics['word_error_rates'].append(wer)
                self.metrics['total_evaluated'] += 1

                print(f"Jaro Similarity: {jaro_distance:.4f}")
                print(f"CER (with transpositions): {cer_osa:.4f}")
                print(f"WER (Word Error Rate): {wer:.4f}")
            else:
                print("Expected Text: [NOT FOUND]")
                print("Result: UNKNOWN")

            print("-" * 50)

    def print_summary_metrics(self):
        if self.metrics['total_evaluated'] > 0:
            print("\n" + "=" * 50)
            print("SUMMARY STATISTICS")
            print("-" * 50)
            print(f"Average Jaro Similarity: {np.mean(self.metrics['jaro_distances']):.4f}")
            print(f"Average CER (with OSA): {np.mean(self.metrics['character_error_rates_osa']):.4f}")
            print(f"Average WER: {np.mean(self.metrics['word_error_rates']):.4f}")
            print(f"Total Images Evaluated: {self.metrics['total_evaluated']}")
            print("=" * 50)

    def plot_metrics(self):
        plt.figure(figsize=(15, 10))

        # Jaro Similarity
        plt.subplot(2, 3, 1)
        plt.scatter(range(len(self.metrics['jaro_distances'])), self.metrics['jaro_distances'], 
                   marker='o', color='green', label='Values')
        avg_jaro = np.mean(self.metrics['jaro_distances'])
        plt.axhline(y=avg_jaro, color='darkgreen', linestyle='--', 
                   label=f'Average: {avg_jaro:.4f}')
        plt.title('Jaro Similarity per sample')
        plt.xlabel('Sample index')
        plt.ylabel('Similarity')
        plt.grid(True)
        plt.legend()
        
        # CER
        plt.subplot(2, 3, 2)
        plt.scatter(range(len(self.metrics['character_error_rates_osa'])), 
                   self.metrics['character_error_rates_osa'], 
                   marker='o', color='red', label='Values')
        avg_cer = np.mean(self.metrics['character_error_rates_osa'])
        plt.axhline(y=avg_cer, color='darkred', linestyle='--', 
                   label=f'Average: {avg_cer:.4f}')
        plt.title('CER per sample')
        plt.xlabel('Sample index')
        plt.ylabel('Error rate')
        plt.grid(True)
        plt.legend()
        
        # WER
        plt.subplot(2, 3, 3)
        plt.scatter(range(len(self.metrics['word_error_rates'])), 
                   self.metrics['word_error_rates'], 
                   marker='x', color='blue', label='Values')
        avg_wer = np.mean(self.metrics['word_error_rates'])
        plt.axhline(y=avg_wer, color='darkblue', linestyle='--', 
                   label=f'Average: {avg_wer:.4f}')
        plt.title('WER per sample')
        plt.xlabel('Sample index')
        plt.ylabel('Error rate')
        plt.grid(True)
        plt.legend()

        # Cumulative averages
        jaro_cumulative_avgs = [np.mean(self.metrics['jaro_distances'][:i+1]) for i in range(len(self.metrics['jaro_distances']))]
        cer_cumulative_avgs = [np.mean(self.metrics['character_error_rates_osa'][:i+1]) for i in range(len(self.metrics['character_error_rates_osa']))]
        wer_cumulative_avgs = [np.mean(self.metrics['word_error_rates'][:i+1]) for i in range(len(self.metrics['word_error_rates']))]
        
        plt.subplot(2, 3, 4)
        plt.plot(jaro_cumulative_avgs, color='green', linestyle='--', label='Cumulative Average')
        plt.axhline(y=avg_jaro, color='darkgreen', linestyle='-', 
                   label=f'Final Average: {avg_jaro:.4f}')
        plt.title('Jaro Average Evolution')
        plt.xlabel('Number of samples')
        plt.ylabel('Average')
        plt.grid(True)
        plt.legend()
        
        plt.subplot(2, 3, 5)
        plt.plot(cer_cumulative_avgs, color='red', linestyle='--', label='Cumulative Average')
        plt.axhline(y=avg_cer, color='darkred', linestyle='-', 
                   label=f'Final Average: {avg_cer:.4f}')
        plt.title('CER Average Evolution')
        plt.xlabel('Number of samples')
        plt.ylabel('Average')
        plt.grid(True)
        plt.legend()
        
        plt.subplot(2, 3, 6)
        plt.plot(wer_cumulative_avgs, color='blue', linestyle='--', label='Cumulative Average')
        plt.axhline(y=avg_wer, color='darkblue', linestyle='-', 
                   label=f'Final Average: {avg_wer:.4f}')
        plt.title('WER Average Evolution')
        plt.xlabel('Number of samples')
        plt.ylabel('Average')
        plt.grid(True)
        plt.legend()
        
        plt.tight_layout()
        plt.show()
