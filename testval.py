import numpy as np
import pandas as pd
import embedding as ebd
import prepare_data
import models
import argparse
import sys
import keras.backend as K
from nltk import word_tokenize
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image
from keras.models import load_model

MAX_LEN = 13

def preprocess_question(question):
	word_idx = ebd.load_idx()
	tokens = word_tokenize(question)
	seq = []
	for token in tokens:
		seq.append(word_idx.get(token,0))
	seq = np.reshape(seq,(1,len(seq)))
	return seq

def get_3D_matrix(captions, embeddings):
    res = [[]]
    for caption in captions:
        sentence = [np.asarray([[0]]*300,dtype='float32')]*MAX_LEN
        words = word_tokenize(caption)
        for i, word in enumerate(words):
            sentence[i] = [[x] for x in embeddings.get(word, np.asarray([0]*300,dtype='float32'))]
        res[0].append(sentence)
    res = np.asarray(res)
    print(res.shape)
    return res

def load_model():
	model_path = 'weights/model_1.h5'
	model = models.vis_lstm()
	model.load_weights(model_path)
	return model

def generate_answers(caption_matrix, question, model):
    # captions_matrix = get_3D_matrix(captions, embeddings)
	seq = preprocess_question(question)
	x = [caption_matrix, seq]
	probabilities = model.predict(x)[0]
	answers = np.argsort(probabilities[:1000])
	top_answers = [prepare_data.top_answers[answers[-1]],
	prepare_data.top_answers[answers[-2]],
	prepare_data.top_answers[answers[-3]]]
	return top_answers

def transf(c):
    c = np.asarray([[x] for x in c])
    c = c.swapaxes(0, 4)
    print(c.shape)
    return c

def evaluate_val():
    val_path = 'data/valv1.pkl'
    # embeddings = prepare_data.load_embeddings()
    model = load_model()
    df = pd.read_pickle(val_path)
    questions = df[['questions']].values.tolist()
    captions_matrix = np.asarray(df[['caption_matrix']].values.tolist())
    captions_matrix = captions_matrix.swapaxes(1,2)
    captions_matrix = captions_matrix.swapaxes(2,3)
    captions_matrix = captions_matrix.swapaxes(3,4)
    captions = df[['captions']].values.tolist()
    answers = df[['answers']].values.tolist()
    image_ids = df[['image_id']].values.tolist()
    question_ids = df[['question_ids']].values.tolist()
    data = {'image_id': [], 'captions': [], 'questions': [], 'answers': [], 'question_ids': [], 'top_answers': []}
    cnt = 0
    for question, caption_matrix, image_id, question_id, answer, caption in zip(questions, captions_matrix, image_ids, question_ids, answers, captions):
        print(cnt)
        question = question[0]
        caption_matrix = np.asarray(caption_matrix)
        # caption_matrix = transf(caption_matrix)
        caption_matrix = np.asarray([caption_matrix])
        print(caption_matrix.shape)
        print(question)
        print(image_id)
        print(question_id)
        print(answer)
        print(caption)
        top_answers = generate_answers(caption_matrix, question, model)
        data['image_id'].append(image_id)
        data['captions'].append(caption)
        data['questions'].append(question)
        data['question_ids'].append(question_id)
        data['answers'].append(answer)
        data['top_answers'].append(top_answers)
        print('Top answers: %s, %s, %s.' % (top_answers[0],top_answers[1],top_answers[2]))
        cnt += 1
    df_new = pd.DataFrame(data=data)
    df_new.to_pickle('test.pkl')

def main():
	evaluate_val()

if __name__ == '__main__':main()