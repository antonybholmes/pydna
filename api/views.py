from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os

from dna import settings

import sys
sys.path.append('/ifs/scratch/cancer/Lab_RDF/abh2138/scripts/python/lib/libhttp/libhttp')
import libhttp
sys.path.append('/ifs/scratch/cancer/Lab_RDF/abh2138/scripts/python/lib/libdna')
import libdna

CHR_SORT_DICT = {'chr1':1,
                 'chr2':2,
                 'chr3':3, 
                 'chr4':4, 
                 'chr5':5, 
                 'chr6':6, 
                 'chr7':7, 
                 'chr8':8, 
                 'chr9':9, 
                 'chr10':10,
                 'chr11':11,
                 'chr12':12,
                 'chr13':13,
                 'chr14':14,
                 'chr15':15,
                 'chr16':16,
                 'chr17':17,
                 'chr18':18,
                 'chr19':19,
                 'chr20':20,
                 'chr21':21,
                 'chr22':22,
                 'chrX':23,
                 'chrY':24,
                 'chrM':25}

def about(request):
    return JsonResponse({'name':'genes','version':'1.0','copyright':'Copyright (C) 2018 Antony Holmes'}, safe=False)

def seq(request):
    """
    Allow users to search for genes by location
    """
    
    # Defaults should find BCL6
    id_map = libhttp.parse_params(request, {'db':'ucsc', 
                                            'g':'grch38', 
                                            'chr':'chr3', 
                                            's':187721377, 
                                            'e':187721577, 
                                            'lc': 0,
                                            'mask':'l',
                                            'rev_comp':0})
    
    db = id_map['db'][0]
    genome = id_map['g'][0]
    
    chr = id_map['chr'][0]
    start = id_map['s'][0]
    end = id_map['e'][0]
    
    mask = id_map['mask'][0]
    rev_comp = id_map['rev_comp'][0] == 1
    lowercase = id_map['lc'][0] == 1
    
    if rev_comp:
        strand = '-'
    else:
        strand = '+'
    
    if start > end:
      start = start ^ end
      end = start ^ end
      start = start ^ end
    
    loc = '{}:{}-{}'.format(chr, start, end)
    
    dir = os.path.join(settings.DATA_DIR, db, genome)
    
    dna = libdna.DNA2Bit(dir)
    
    seq = dna.dna(loc, mask=mask, rev_comp=rev_comp, lowercase=lowercase)
    
    return JsonResponse({'genome':genome, 'loc':loc, 'strand':strand, 'seq':seq}, safe=False)


def genomes(request):
    """
    Allow users to search for genes by location
    """
    
    files = os.listdir(settings.DATA_DIR)
    
    ret = []
    
    for file in files:
        d = os.path.join(settings.DATA_DIR, file)
        if os.path.isdir(d):
            db = file
            
            for file2 in os.listdir(d):
                d2 = os.path.join(d, file2)
                
                if os.path.isdir(d2):
                    genome = file2
                    
                    ret.append({'db':db, 'genome':genome})
    
    return JsonResponse(ret, safe=False)
  
def genome(request):
    """
    Provide details about a genome
    """
    
    id_map = libhttp.parse_params(request, {'db':'ucsc', 'g':'grch38'})
    
    db = id_map['db'][0]
    genome = id_map['g'][0]
    
    dir = os.path.join(settings.DATA_DIR, db, genome)
    
    """
    Allow users to search for genes by location
    """
    files = sorted(os.listdir(dir))
    
    chrs = {}
    
    for file in files:
        f = os.path.join(dir, file)
        
        if os.path.isfile(f) and 'chr' in f and 'size.txt' in f:
            chr = file.split('.')[0]
            
            r = open(f, 'r')
            size = int(r.readline())
            r.close()
            
            idx = CHR_SORT_DICT[chr]
            
            chrs[idx] = {'db':db, 'genome':genome, 'chr':chr, 'size':size}
    
    ret = []
    
    for idx in sorted(chrs):
        ret.append(chrs[idx])
    
    return JsonResponse(ret, safe=False)