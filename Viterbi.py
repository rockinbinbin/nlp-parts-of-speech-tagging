# Assignment 1
# Robin Mehta
#robimeht

from __future__ import division, print_function
import numpy as np 
import sys
import string
import operator
from collections import defaultdict

tagCounts = dict() #unigram tags
test_sentences = [] # sentences for test data

def parse_data_set(path):
	uniqueWords = defaultdict(list) #keys are unique words, values are lists of tags
	tagTransitionDict = dict() #bigram tags
	with open(path,'r') as data:
		numSentences = 0
		for line in data.read().split('\n'):
			if len(line) > 2: # handles empty lines properly
				numSentences += 1
				tagsInSentence = []

				for phrase in line.split(" "):
					if len(phrase) > 1:
						tag = phrase.split("/")[1]
						tagsInSentence.append(tag)
						word = phrase.split("/")[0]
						# if not word in uniqueWords:
						uniqueWords[word].append(tag)
				count = 0
				for x in tagsInSentence:
					if not x in tagCounts:
						tagCounts[x] = 1
					else:
						tagCounts[x] = tagCounts[x] + 1
					if count < len(tagsInSentence):
						if count == 0:
							startOfSentence = '<s>'
							label = startOfSentence + ' ' + tagsInSentence[count]
						else: 
							label = tagsInSentence[count - 1] + ' ' + tagsInSentence[count]
						if not label in tagTransitionDict:
							tagTransitionDict[label] = 1
						else:
							tagTransitionDict[label] = tagTransitionDict[label] + 1
					count = count + 1

	for key in tagTransitionDict:
		unigram = key.split(" ")[0]
		if unigram != '<s>':
			probability = tagTransitionDict[key] / tagCounts[unigram]
			tagTransitionDict[key] = probability
		else:
			probability = tagTransitionDict[key] / numSentences #if "<s> tag" bigram, then divide that by numSentences
			tagTransitionDict[key] = probability

	# sorted_x = sorted(tagTransitionDict.items(), key=operator.itemgetter(1))

	return tagTransitionDict, uniqueWords

test_tags = []
predictedTags = []

def parse_test_set(path):
	testSet = []
	with open(path, 'r') as data:
		for line in data.read().split('\n'):
			if len(line) > 2: # handles empty lines properly
				phrases = []
				for phrase in line.split(" "):
					testSet.append(phrase.split("/")[0])
					if len(phrase) > 2:
						test_tags.append(phrase.split("/")[1])
					phrases.append(phrase.split("/")[0])
			test_sentences.append(phrases)
	return testSet

def runViterbi(tagTransitionDict, wordLists, test_set):
	scoreOfTagsPerWord = dict()
	prevTagScores = dict()
	f = open('POS.test.out', 'a')
	tagForPrevWord = ''
	for sentence in test_sentences:
		for word in sentence:
			f.write(word)
			f.write("/")
			if word in wordLists:
				wordTags = wordLists[word]
			else:
				wordTags.append('NN')

			wordGivenTags = dict() #will store probability of word given tag, with key being tag
			for tag in wordTags: #traverse only through possible tags for that word
				if not tag in wordGivenTags:
					numTagsForWord = wordTags.count(tag)
					numTagsOverall = tagCounts[tag]
					probWordGivenTag = numTagsForWord / numTagsOverall
					wordGivenTags[tag] = probWordGivenTag

			tagGivenTags = dict() #will store probabilites of tag given <s>, with key being tag
			for tag in wordTags:
				if not tag in tagGivenTags:
					scoresPerNewTag = dict() 
					if word == sentence[0]:
						startOfSentenceBigramLabel = "<s> " + tag
					else:
						#figure out previous tag: max
						for prevTag in scoreOfTagsPerWord[prevWord]:
							startOfSentenceBigramLabel = tag + " " + prevTag
							scoresPerNewTag[startOfSentenceBigramLabel] = 0 #add bigram tags to new dict

					if startOfSentenceBigramLabel in tagTransitionDict:
						tagProb = tagTransitionDict[startOfSentenceBigramLabel]

						if startOfSentenceBigramLabel in scoresPerNewTag:
							if prevTag in prevTagScores:
								scoresPerNewTag[startOfSentenceBigramLabel] = tagProb * prevTagScores[prevTag]
					else:
						tagProb = 0 #if bigram '<s> + tag' doesn't exist in tagTransitionDict

					maxScore = 0
					if not word == sentence[0]:
						for newTag in scoresPerNewTag:
							#find max for the tag
							if scoresPerNewTag[newTag] > maxScore:
								maxScore = score
								maxScoreTag = newTag
					#assign tag probabilities to a new array of this current word's tags and scores.
						tagGivenTags[tag] = maxScore
					else:
						tagGivenTags[tag] = tagProb

			tagsAndScores = dict()
			for tag in wordTags:
				if not tag in tagsAndScores:
					score = wordGivenTags[tag] * tagGivenTags[tag]
					tagsAndScores[tag] = score

			scoreOfTagsPerWord[word] = tagsAndScores
			prevWord = word
			prevWordMaxTag = tagsAndScores.keys()[0]

			maxPrevScore = 0
			for tag in tagsAndScores:
				if tagsAndScores[tag] > maxPrevScore:
					prevWordMaxTag = tag
			if not prevWordMaxTag == ')':
				predictedTags.append(prevWordMaxTag)
				f.write(prevWordMaxTag)
				f.write(" ")
			prevTagScores = tagsAndScores
		f.write("\n")

def calculateAccuracy():
	index = 0
	numCorrect = 0
	for tag in predictedTags:
		if tag == test_tags[index]:
			numCorrect += 1
		index += 1
	accuracy = numCorrect / len(test_tags)
	print("Accuracy of the system: ", accuracy, "%")

def main():
	tagTransitionDict, wordLists = parse_data_set(sys.argv[1])
	test_set = parse_test_set(sys.argv[2])
	runViterbi(tagTransitionDict, wordLists, test_set)
	calculateAccuracy()

if __name__ == '__main__':
	main()
