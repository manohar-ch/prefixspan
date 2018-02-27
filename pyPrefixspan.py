import fileinput


counter = 0
class Prefixspan:
    def __init__(self, db = []):
        self.db = db
        self.genSdb()
        
    def genSdb(self):
        '''
        Generate mutual converting tables between db and sdb 
        '''
        self.db2sdb = dict()
        self.sdb2db = list()
        count = 0
        self.sdb = list()
        for seq in self.db:
            newseq = list()
            for item in seq:
                if self.db2sdb.has_key(item):
                    pass
                else:
                    self.db2sdb[item] = count
                    self.sdb2db.append(item)
                    count += 1
                newseq.append( self.db2sdb[item] )
            self.sdb.append( newseq )
        self.itemCount = count
    
    def run(self, min_sup = 2):
        '''
        mine patterns with min_sup as the min support threshold
        '''
        self.min_sup = min_sup
        L1Patterns = self.genL1Patterns()
        patterns = self.genPatterns( L1Patterns )
        self.sdbpatterns = L1Patterns + patterns

    def getPatterns(self):
        '''
        returns the set of the patterns, which is a list of
        tuples (sequence, support)
        '''
        oriPatterns = list()
        for (pattern, sup, pdb) in self.sdbpatterns:
            oriPattern = list()
            for item in pattern:
                oriPattern.append(self.sdb2db[item])
            oriPatterns.append( (oriPattern, sup) )
        return oriPatterns
        
    def genL1Patterns(self):
        '''
        generate length-1 patterns
        '''
        pattern = []
        sup = len(self.sdb)
        pdb = [(i,0) for i in range(len(self.sdb))]
        L1Prefixes = self.span( (pattern, sup, pdb) )
        return L1Prefixes
    
    def genPatterns(self, prefixes):
        '''
        generate length-(l+1) patterns from
        length-l patterns
        '''
        results = []
        for prefix in prefixes:
            result = self.span(prefix)
            results += result
        if results != []:
            results += self.genPatterns( results )
        return results
    
    def span(self, prefix):
        '''
        span current length-l prefix pattern set
        to length-(l+1) prefix pattern set.
        prefix is a tuple (pattern, sup, pdb):
        pattern is an list representation of the pattern,
        sup is the absolute support of the pattern,
        pdb is the projection database of the pattern, 
        which is a list of tuples in the form of (sid,pos).
        '''
        (pattern, sup, pdb) = prefix
        itemSups = [0] * self.itemCount
        for (sid, pid) in pdb:
            itemAppear = [0] * self.itemCount
            for item in self.sdb[sid][pid:]:
                itemAppear[item] = 1
            itemSups = map(lambda x,y: x+y, itemSups, itemAppear)
        prefixes = list()
        for i in range(len(itemSups)):
            if itemSups[i] >= self.min_sup:
                newPattern = pattern + [i]
                newSup = itemSups[i]
                newPdb = list()
                for (sid, pid) in pdb:
                    for j in range(pid, len(self.sdb[sid])):
                        item = self.sdb[sid][j]
                        if item == i:
                            newPdb.append( (sid, j+1) )
                            break
                prefixes.append( (newPattern, newSup, newPdb) )
                #self.span( (newPattern, newSup, newPdb) )
        return prefixes
         
def mine(inputfile, outputfile, supportCt):
    sdb = []
    
    lines = fileinput.input(inputfile)
    for line in lines:
        try:
            line1=line.split()[0]
            seq = line1.split(',')
            sdb.append( seq )
        except:
            continue
    
    support = int(len(sdb)*float(supportCt/100))
 
    span = Prefixspan(sdb)
    span.run(support)
    patterns = span.getPatterns()
    
    return patterns
#    f = open(outputfile, 'w')
#    count = 0;
#    for pattern in patterns:
#        #print '{' + str(pattern) + '}'
#        f.write( str(pattern) + '\n' )
#        count = count + 1;
#    f.close()
#    print "Total rules: %s" %count
        
def test():
    db = [[0,1,2,3,4], [0,1,2,3],[3,2,1,2,1,2],[1,2,3,2,3,1],[1,2,3,1,0,1]]
    span = Prefixspan(db)
    span.run(2)
    print span.getPatterns()
    
def displayUsage():
    print '''
    Usage:
    1. run dummy test
    python pyPrefixspan.py test
    2. 
    python pyPrefixspan.py input_file_name output_file_name support_threshold
    
    All rights reserved.
    http://datamininginsight.blogspot.com
    '''

def proceed(freq_seqs):
    
    ruleset = []
    global counter
    lth = 1
    
    for seq, support in freq_seqs:
        print seq, " - ", support
        if len(seq) > lth:
            counter += 1
            lth = len(seq)
        if len(seq) > 1:
            ruleset.append((seq[:-1],seq[-1:],support)) 
                
    holder = buildDataStruct(ruleset)
    file = "F:\Uni\Final Year Project\Data\sessions6.csv"
    #file = "C:\Users\Gokul\Desktop\enaeseth-python-fp-growth-0.1.1-5-g5803128\enaeseth-python-fp-growth-5803128\samp.txt"
    prefixspanRecommender(file, holder)    


def buildDataStruct(seqs):
    print '\n >--> in progress <--<'
    holder = dict()
    ct = 0
    while ct <= counter:
        ct +=1
        holder[ct] = dict()
        
    for ant, con, sup in seqs:
        length = len(ant)
        seq = holder[length]
        antecedent = tuple(ant)
        consequent = tuple(con)
        if seq.has_key(antecedent):
            opt = seq.get(antecedent)
            opt[consequent] = sup
        else:
            opt = dict()
            opt[consequent] = sup
            seq[antecedent] = opt
            
    return holder
    
def evaluate(recommendationSet,actual,average,count,correct):
    count+=1
    if actual in recommendationSet:
        average = calculateAccuracy(1,average,count)
        #print 'CORRECT'
        correct+=1
        return (average,count,correct)
    else:
        average=calculateAccuracy(0,average,count)
        #print 'INCORRECT'
        return (average,count,correct)
    
def calculateAccuracy(correct,average,count):
        return ((int(count)-1)*float(average)+int(correct))*100/int(count)

              
def recommend(session, holder):
    sessionSet = tuple(session)
    length = len(session)
    if length > len(holder):
        return ""
    ruleSet = holder[length]
    if ruleSet.has_key(sessionSet):
        resultSet = ruleSet[sessionSet]
        recommendlist= []
        for key,item in resultSet.items():
            recommendlist.append(tuple(key))
        return recommendlist
    return ""

    
def prefixspanRecommender(sessions, holder):
    
    file_iter = open(sessions, 'rU')
    count=0
    average=0
    total = 0
    correct =0
    print "Recommender : ", 1
    
    for line in file_iter:
        linex = line.strip().rstrip(',')
        elem = linex.split(',')
        iterator =0
        sessionList =[]
        if len(elem)>1:
            for item in elem:
                iterator +=1
                print "Recommender Iterator : ", iterator
                if iterator==(len(elem)-1):
                    break
                sessionList.append(item)
                print "Recommender session : ", sessionList
                recommendationList = recommend(sessionList, holder)
                total+=1
                print "Recommender recommendation : ", recommendationList
                if not (len(recommendationList)<1):
                    result= evaluate(recommendationList, tuple([elem[iterator]]), average, count,correct)
                    average=result[0] 
                    count=result[1] 
                    correct=result[2]
                else:
                    print "No valid recommendation"
                    
    if not (count == 0 or total == 0):                
        accuracy = float(correct)/float(count)
        coverage = float(count)/float(total)
        print "Average : ", average
        print "Total : ",total
        print "Count : ", count
        print "Correct : ", correct
        print "Accuracy : , %.3f" % (accuracy*100)
        print "Coverage : , %.3f"  % (coverage*100)
        
    
def main():
    from sys import argv
    if len(argv) == 2 and argv[1].lower() == 'test':
        test()
    elif len(argv) == 4:
        min_sup = 2
        try:
            min_sup = float(argv[3])
            print min_sup
        except:
            displayUsage()
        else:
            #freq_seqs = mine(argv[1], argv[2], min_sup)
            source = "F:\Uni\Final Year Project\Data\sessions5.csv"
            freq_seqs = mine(source, argv[2], min_sup)
            proceed(freq_seqs)
            
    else:
        displayUsage()
    

if __name__ == "__main__":
    main()
    