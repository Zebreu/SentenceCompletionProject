import numpy as np

questions_path = "C:\\Users\\Sebastien\\Projet\\MSR_Sentence_Completion_Challenge_V1\\Data\\Holmes.lm_format.questions.preprocessed.txt"

questions = open(questions_path)

sentences = []

for line in questions:
    sentences.append(line.split(' ')[1:-2])

different_word_index = np.zeros((1040), dtype = np.int)
for question_number in xrange(1040):
    sen_0 = sentences[5*question_number]
    sen_1 = sentences[5*question_number+1]
    sentence_length = len(sen_0)
    for i in xrange(sentence_length):
        if sen_0[i]!=sen_1[i]:
            different_word_index[question_number] = i
            continue

answers_path = "C:\\Users\\Sebastien\\Projet\\MSR_Sentence_Completion_Challenge_V1\\Data\\Holmes.lm_format.answers.preprocessed.txt"

answer_file = open(answers_path)

answer_list = []

for line in answer_file:
    answer_list.append(line.split(' ')[1:-1])

answers = np.zeros((1040))

for question_number in xrange(1040):
    for i in xrange(5):
        if answer_list[question_number][different_word_index[question_number]] == sentences[5*question_number+i][different_word_index[question_number]]:
            answers[question_number] = i
            continue

best_result = 0
best_param_1 = 0
best_param_2 = 0
best_scores = np.zeros((1040,5))

for param_1 in [0.,-1/10.,-1/9.,-1/8.,-1/7.,-1/6.,-1/5.,-1/4.,-1/3.,-1/2.,-1.,-2.,-3.,-10.]:
    for param_2 in [1,2,3,4,5,6,7,8,9,10,20,50,100]:
        scores = np.zeros((1040,5))
        for question_number in xrange(1040):
            sen_0 = sentences[5*question_number]
            sentence_length = len(sen_0)
            for i in xrange(5):
                different_word = sentences[5*question_number+i][different_word_index[question_number]]
                if model.__contains__(different_word):
                    for j in xrange(sentence_length):
                        if j != different_word_index[question_number] and model.__contains__(sen_0[j]):
                            scores[question_number,i] += pow(model.vocab[sen_0[j]].count,param_1)*((model.similarity(different_word,sen_0[j])+1)**param_2) #to have non-negative scores

        scores_amax = np.argmax(scores,1)

        correct = 0

        for question_number in xrange(1040):
            if scores_amax[question_number] == answers[question_number]:
                correct += 1

        final_score = correct/1040.
        if final_score > best_result:
            best_result = final_score
            best_param_1 = param_1
            best_param_2 = param_2
            best_scores = scores.copy()

print best_result, best_param_1, best_param_2