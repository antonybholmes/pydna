from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os

from dna import settings

import sys
import libhttp
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
    return JsonResponse(settings.ABOUT, safe=False)

def seq(request):
    """
    Allow users to search for genes by location
    """
    
    # Defaults should find BCL6
    id_map = libhttp.parse_params(request, {'n':'human', 
                                            'a':'grch38', 
                                            't': 'ucsc',
                                            'chr':'chr3', 
                                            's':187721357, 
                                            'e':187721577,
                                            'pad5':0,
                                            'pad3':0,
                                            'lc': 0,
                                            'mask':'l',
                                            'rev_comp':0,
                                            'mode':'json'})
    
    name = id_map['n'][0]
    assembly = id_map['a'][0]
    track = id_map['t'][0]
    
    chr = id_map['chr'][0]
    start = id_map['s'][0]
    end = id_map['e'][0]
    
    pad5 = max(0, id_map['pad5'][0])
    pad3 = max(0, id_map['pad3'][0])
    
    mask = id_map['mask'][0]
    rev_comp = id_map['rev_comp'][0] == 1
    lowercase = id_map['lc'][0] == 1
    
    mode = id_map['mode'][0]
    
    if rev_comp:
        strand = '-'
    else:
        strand = '+'
    
    if start > end:
      start = start ^ end
      end = start ^ end
      start = start ^ end
    
    loc = libdna.Loc(chr, start, end)
    
    if pad5 > 0 or pad3 > 0:
        loc = libdna.Loc(loc.chr, loc.start - pad5, loc.end + pad3)
        
    #dir = os.path.join(settings.DATA_DIR, name, assembly, track)
    #dna = libdna.DNA2Bit(dir)
    
    dir = os.path.join('dna', name, assembly, track).lower()
    print(dir, file=sys.stderr)
    dna = libdna.AWSS3DNA2Bit(settings.AWS_BUCKET, dir)
    
    
    seq = dna.dna(loc, mask=mask, rev_comp=rev_comp, lowercase=lowercase)
    
    if mode == 'text':
        return HttpResponse('>genome={} location={} strand={} pad5={} pad3={} mask={}\n{}'.format(genome, loc.__str__(), strand, pad5, pad3, mask, seq), content_type="text/plain")
    elif mode == 'fasta':
        return HttpResponse('>genome={} location={} strand={} pad5={} pad3={} mask={}\n{}'.format(genome, loc.__str__(), strand, pad5, pad3, mask, libdna.format_dna(seq)), content_type="text/plain")
    else:
        return JsonResponse({'name':name, 'assembly':assembly, 'track':track, 'loc':loc.__str__(), 'strand':strand, 'seq':seq, 'mask':mask, 'pad5':pad5, 'pad3':pad3}, safe=False)
        
    


def genomes(request):
    """
    Allow users to search for genes by location
    """
    
#    names = os.listdir(settings.DATA_DIR)
#    
#    ret = []
#    
#    for name in names:
#        d = os.path.join(settings.DATA_DIR, name)
#        
#        if os.path.isdir(d):
#            for assembly in os.listdir(d):
#                d2 = os.path.join(d, assembly)
#                
#                if os.path.isdir(d2):
#                    for track in os.listdir(d2):
#                        d3 = os.path.join(d2, track)
#                        
#                        if os.path.isdir(d3):
#                            ret.append({'name':name, 'assembly':assembly, 'track':track})
#    
#    
#    s3 = boto3.client('s3')
#    #bucket = s3.Bucket(settings.AWS_BUCKET)
#    
#    
#    #for file in bucket.objects.filter(Delimiter='/', Prefix='dna/human/'):
#    #    print(file.key, file=sys.stderr)
#    
#    
#    paginator = s3.get_paginator('list_objects_v2')
#    
#    for page in paginator.paginate(Bucket=settings.AWS_BUCKET, Prefix='dna/', Delimiter="/"):
#       for obj in page['Contents']: #.filter(Prefix="dir_name/"):
#           print(obj['Key'], file=sys.stderr)
#    
#    
#    ret={}
    return JsonResponse(settings.GENOMES, safe=False)
  
def genome(request):
    """
    Provide details about a genome
    """
    
    id_map = libhttp.parse_params(request, {'n':'human', 't':'ucsc', 'a':'grch38'})
    
    name = id_map['n'][0]
    assembly = id_map['a'][0]
    track = id_map['t'][0]
    
    dir = os.path.join(settings.DATA_DIR, name, assembly, track)
    
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
            
            chrs[idx] = {'name':name, 'assembly':assembly, 'track':track, 'chr':chr, 'size':size}
    
    ret = []
    
    for idx in sorted(chrs):
        ret.append(chrs[idx])
    
    return JsonResponse(ret, safe=False)