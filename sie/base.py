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

class RelationExtractor(object):
    
    def __init__(self, cnlp):
        self.cnlp = cnlp
        
    def isMentioned(self, sentence):
        raise NotImplementedError("Subclasses should override.")
        
    def extract(self, sentence):
        extraction = [] 
        if self.isMentioned(sentence):
            subSentences, trees, coref = self.cnlp.parse(sentence)
            if subSentences is not None and trees is not None:
                for tree in trees:
                    extraction += self._extractFromTreeRecursive(tree)
            else:
                print "Error anslyzing sentence: \"%s\"" % sentence
        return extraction
    
    def _extractFromTreeRecursive(self, tree):
        extraction = []
        if isinstance(tree, nltk.tree.Tree):
            extraction += self._extractFromSingleTree(tree)
            for subTree in tree:
                extraction += self._extractFromTreeRecursive(subTree)
        return extraction
    
    def _extractFromSingleTree(self, tree):
        raise NotImplementedError("Subclasses should override.")
        
class AggregateExtractor(RelationExtractor):
    
    def __init__(self, cnlp):
        super(AggregateExtractor, self).__init__(cnlp)
        self.extractors = self.makeExtractors(cnlp)
    
    def makeExtractors(self):
        raise NotImplementedError("Subclasses should override.")
        
    def isMentioned(self, sentence):
        for extractor in self.extractors:
            if extractor.isMentioned(sentence):
                return True
        return False
    
    def extract(self, sentence):
        extraction = []
        for extractor in self.extractors:
            extraction += extractor.extract(sentence)
        return extraction
