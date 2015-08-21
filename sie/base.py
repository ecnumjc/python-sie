import os
import sys
import re
import collections

import nltk.tree
import pattern.en

import ashlib.util.str_
import ashlib.util.list_
import ashlib.ling.cnlp
import ashlib.ling.trees
import ashlib.ling.tokenize

## standard parsers #######################################################################################

def cnlpParser(cnlp):
    def parser(text):
        sentences = []
        
        initialSentences = ashlib.ling.tokenize(text)
        for sentence in initialSentences:
            subSentences, trees, coref = cnlp.parse(sentence)
            if subSentences is not None and trees is not None:
                for index, subSentence in enumerate(subSentences):
                    sentences.append((subSentence, trees[index]))

        return sentences

    return parser

def mapParser(): ## TODO: maybe not necessary
    map = {}
    parser = lambda text: map[text]
    return (parser, map)

## RelationExtractor #####################################################################################

class RelationExtractor(object):
    
    def __init__(self, parser):
        self.parser = parser
        
    def isMentioned(self, text):
        raise NotImplementedError("Subclasses should override.")
        
    def extract(self, text):
        relations = []
        if self.isMentioned(text):
            for sentence, tree in self.parser(text):
                relations += self._extractFromPlainText(sentence)
                relations += self._extractFromTreeRecursive(tree)
            else:
                print "Error anslyzing sentence: \"%s\"" % sentence
        return relations
    
    def _extractFromPlainText(self, sentence):
        raise NotImplementedError("Subclasses should override.")
    
    def _extractFromTreeRecursive(self, tree):
        extraction = []
        if isinstance(tree, nltk.tree.Tree):
            extraction += self._extractFromSingleTree(tree)
            for subTree in tree:
                extraction += self._extractFromTreeRecursive(subTree)
        return extraction
    
    def _extractFromSingleTree(self, tree):
        raise NotImplementedError("Subclasses should override.")

## AggregateExtractor ####################################################################################
        
class AggregateExtractor(RelationExtractor):
    
    def __init__(self, parser):
        super(AggregateExtractor, self).__init__(parser)
        self.extractors = self.makeExtractors()
    
    def makeExtractors(self):
        raise NotImplementedError("Subclasses should override.")
        
    def isMentioned(self, text):
        for extractor in self.extractors:
            if extractor.isMentioned(text):
                return True
        return False
    
    def extract(self, text):
        extraction = []
        for extractor in self.extractors:
            extraction += extractor.extract(text)
        return extraction
