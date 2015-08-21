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

## HyponymPatternExtractor #################################################################################

class HyponymPatternExtractor(base.RelationExtractor):
    
    def __init__(self, parser, hypernyms):
        super(HyponymPatternExtractor, self).__init__(parser)
        self.hypernyms = hypernyms
    
    def isMentioned(self, text):
        for synonym in self.hypernyms:
            if synonym in text:
                return True
        return False

## HyponymIsHypernymExtractor ##############################################################################
    
class HyponymIsHypernymExtractor(HyponymPatternExtractor):
    
    ## TODO: expand isMentioned and _extractFromSingleTree to look for tenses of "to be" besides just "is". Phrasal conjugations may require reworking the code a little to add phrasal support.
    
    def isMentioned(self, text):
        return super(HyponymIsHypernymExtractor, self).isMentioned(text) and "is" in text
    
    def _extractFromPlainText(self, sentence):
        return []
    
    def _extractFromSingleTree(self, tree):
        relations = []
        
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
                            relations.append(subTree) ## TODO: consider just returnign the tree for later analysis
                            
        return relations

## HypernymNamedHyponymExtractor ###########################################################################

class HypernymNamedHyponymExtractor(HyponymPatternExtractor):
    
    def namedSynonyms(self):
        ## TODO: extend (potentially to phrases like "is known as") that may require reworking the code to work with phrases.
        return ["called", "named", "titled", "denominated", "dubbed", "entitled", "labeled",
                "designated", "termed"]
    
    def isMentioned(self, text):
        if not super(HypernymNamedHyponymExtractor, self).isMentioned(text):
            return False
        for synonym in self.namedSynonyms():
            if synonym in text:
                return True
        return False
    
    def _extractFromPlainText(self, sentence):
        return []
    
    def _extractFromSingleTree(self, tree):
        relations = []
        
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
                            relations.append(nextSubtree[1])
                    
        return relations

## HyponymCommaHypernymExtractor ###########################################################################
    
class HyponymCommaHypernymExtractor(HyponymPatternExtractor):
    
    def _extractFromPlainText(self, sentence):
        return []
    
    def _extractFromSingleTree(self, tree):
        relations = []
        
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
                    relations.append(firstSubTree)
        
        return relations

## HypernymCommaHyponymExtractor ###########################################################################
    
class HypernymCommaHyponymExtractor(HyponymPatternExtractor):
    
    def _extractFromPlainText(self, sentence):
        return []
    
    def _extractFromSingleTree(self, tree):
        relations = []
        
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
                    relations.append(thirdSubTree)
        
        return relations

## HyponymExtractor ########################################################################################

class HyponymExtractor(base.AggregateExtractor):

    def __init__(self, parser, hypernyms):
        self.hypernyms = hypernyms
        super(HyponymExtractor, self).__init__(parser)
        
    def makeExtractors(self):
        [sie.hypernyms.HyponymIsHypernymExtractor(self.parser, self.hypernyms),
         sie.hypernyms.HypernymNamedHyponymExtractor(self.parser, self.hypernyms),
         sie.hypernyms.HyponymCommaHypernymExtractor(self.parser, self.hypernyms),
         sie.hypernyms.HypernymCommaHyponymExtractor(self.parser, self.hypernyms)]
