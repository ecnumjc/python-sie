import os
import sys
import re
import collections

import nltk.tree
import pattern.en
import ashlib.ling.trees

import base

## TODO: would be good to add some sample sentences that conform to these pattern as comments for clarity.
## TODO: These names would be ambiguous with hypernym extractors with the same patterns. Could consider changing the names to not reflect the patterns, or inserting "Hyponym" before "Extractor" in each name (although that would make them really long).

## HyponymExtractor ########################################################################################

class HyponymExtractor(base.RelationExtractor):
    
    def __init__(self, cnlp, hypernyms):
        super(HyponymExtractor, self).__init__(cnlp)
        self.hypernyms = hypernyms
    
    def isMentioned(self, sentence):
        for synonym in self.hypernyms:
            if synonym in sentence:
                return True
        return False

## HyponymIsHypernymExtractor ##############################################################################
    
class HyponymIsHypernymExtractor(HyponymExtractor):
    
    ## TODO: expand isMentioned and _extractFromSingleTree to look for tenses of "to be" besides just "is". Phrasal conjugations may require reworking the code a little to add phrasal support.
    
    def isMentioned(self, sentence):
        return super(IsHypernymExtractor, self).isMentioned(sentence) and "is" in sentence
    
    def _extractFromSingleTree(self, tree):
        extraction = []
        
        def indicatesHyponym(tree):
            nounPhrase = ashlib.ling.trees.toString(ashlib.ling.trees.prune(tree, 1))
            for synonym in self.hypernyms:
                # Note that we insert an article before the synonym
                if nounPhrase.startswith(pattern.en.referenced(synonym)):
                    return True
            
            if len(tree) > 0:
                nounPhrase = ashlib.ling.trees.toString(tree[0])
                for synonym in self.hypernyms:
                    if nounPhrase.endswith(synonym):
                        return True
                
            return False
        
        for index in range(len(tree) - 1):
            subTree = tree[index]
            nextSubtree = tree[index + 1]
            
            ## TODO: could reuquire first phrase to be a NP, but that wouldn't work well with proper nouns
            if ashlib.ling.trees.posMatches(nextSubtree, "VP"):
                if len(nextSubtree) >= 2:
                    if ashlib.ling.trees.wordMatches(nextSubtree[0], "is"): ## TODO: later could add in other tenses of to be
                        if indicatesHyponym(nextSubtree[1]):
                            extraction.append(subTree) ## TODO: consider just returnign the tree for later analysis
                            
        return extraction

## HypernymNamedHyponymExtractor ###########################################################################

class HypernymNamedHyponymExtractor(HyponymExtractor):
    
    def isMentioned(self, sentence):
        if not super(HypernymNamedExtractor, self).isMentioned(sentence):
            return False
        for synonym in self.namedSynonyms():
            if synonym in sentence:
                return True
        return False
    
    def namedSynonyms(self):
        return ["called", "named", "titled", "denominated", "dubbed", "entitled", "labeled", 
                "designated", "termed"] ## TODO: extend (potentially to phrases like "is known as") that may require reworking the code to work with phrases.
    
    def _extractFromSingleTree(self, tree):
        extraction = []
        
        def isNamedSynonym(tree):
            for synonym in self.namedSynonyms():
                if ashlib.ling.trees.wordMatches(tree, synonym):
                    return True
                
            return False
        
        def indicatesHyponym(tree):
            if ashlib.ling.trees.posMatches(tree, lambda tag: tag == "NP" or tag == "S"):
                nounPhrase = ashlib.ling.trees.toString(tree)
                for synonym in self.hypernyms:
                    if nounPhrase.endswith(synonym):
                        return True
            return False
        
        for index in range(len(tree) - 1):
            subTree = tree[index]
            nextSubtree = tree[index + 1]
            
            if indicatesHyponym(subTree):    
                if ashlib.ling.trees.posMatches(nextSubtree, "VP"):
                    if len(nextSubtree) >= 2:
                        if isNamedSynonym(nextSubtree[0]):
                            extraction.append(nextSubtree[1])
                    
        return extraction

## HyponymCommaHypernymExtractor ###########################################################################
    
class HyponymCommaHypernymExtractor(HyponymExtractor):
    
    def _extractFromSingleTree(self, tree):
        extraction = []
        
        def indicatesHyponym(tree):
            if ashlib.ling.trees.posMatches(tree, lambda tag: tag == "NP" or tag == "S"):
                nounPhrase = ashlib.ling.trees.toString(tree)
                for synonym in self.hypernyms:
                    if nounPhrase.endswith(synonym):
                        return True
            return False
        
        def indicatesHyponymRecursive(tree):
            if indicatesHyponym(tree):
                return True
            elif isinstance(tree, nltk.tree.Tree) and len(tree) > 0:
                return indicatesHyponymRecursive(tree[0])
            else: 
                return False
            
        for index in range(len(tree) - 2):
            firstSubTree = tree[index]
            secondSubStree = tree[index + 1]
            thirdSubTree = tree[index + 2]
            
            if ashlib.ling.trees.wordMatches(secondSubStree, ","):
                if indicatesHyponymRecursive(thirdSubTree):
                    extraction.append(firstSubTree)
        
        return extraction

## HypernymCommaHyponymExtractor ###########################################################################
    
class HypernymCommaHyponymExtractor(HyponymExtractor):
    
    def _extractFromSingleTree(self, tree):
        extraction = []
        
        def indicatesHyponym(tree):
            if ashlib.ling.trees.posMatches(tree, lambda tag: tag == "NP" or tag == "S"):
                nounPhrase = ashlib.ling.trees.toString(tree)
                for synonym in self.hypernyms:
                    if nounPhrase.endswith(synonym):
                        return True
            return False
        
        for index in range(len(tree) - 2):
            firstSubTree = tree[index]
            secondSubStree = tree[index + 1]
            thirdSubTree = tree[index + 2]
            
            if ashlib.ling.trees.wordMatches(secondSubStree, ","):
                if indicatesHyponym(firstSubTree):
                    extraction.append(thirdSubTree)
        
        return extraction
