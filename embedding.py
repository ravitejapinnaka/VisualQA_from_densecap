import numpy as np
import h5py
import pickle
import argparse

def load():
	path = 'embeddings/embedding_matrix.h5'
	with h5py.File(path,'r') as hf:
		data = hf.get('embedding_matrix')
		embedding_matrix = np.array(data)
	return embedding_matrix

def load_idx():
	path = 'embeddings/word_idx_1'
	with open(path,'rb') as file:
		word_idx = pickle.load(file)
	return word_idx

def create(glove_path):
	embedding_matrix_path = 'embeddings/embedding_matrix.h5'
	word_idx_path = 'embeddings/word_idx'
	embeddings = {}
	word_idx = {}

	cnt = 0
	with open(glove_path,'r') as f:
		for i, line in enumerate(f):
			values = line.split()
			word = values[0]
			try:
				coefs = np.asarray(values[1:],dtype='float32')
			except Exception as ex:
				cnt += 1
				print("ex:{}/i:{}".format(cnt, i))
				continue
			embeddings[word] = coefs
			word_idx[word] = i+1

	num_words = len(word_idx)
	embedding_matrix = np.zeros((1+num_words,300))

	cnt = 0
	for i, word in enumerate(word_idx.keys()):
		try:
			embedding_matrix[i+1] = embeddings[word]
		except:
			cnt += 1
			print("ex:{}/i:{}".format(cnt, i))
			continue

	with h5py.File(embedding_matrix_path, 'w') as hf:
		hf.create_dataset('embedding_matrix',data=embedding_matrix)

	with open(word_idx_path,'w') as f:
		pickle.dump(word_idx,f)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-address', type=str, required=True)
	args = parser.parse_args()
	print('Preparing embeddings ...')
	create(args.address)

if __name__ == '__main__': main()
