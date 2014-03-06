#!/usr/bin/python

from itertools import izip
import yaml
#import sys
import json


def buildChildStructure(name, data, sdata, colors):
    child = {}
    child['name'] = name
    child['children'] = []
    child['color'] = str(colors[0])
    color = colors[1:]
    if not color:
        color = colors
    if type(data) is list:
        for k in data:
            size = int(sdata.get(k, 0))
            sdata[k] = 0
            if size != 0:
                child['children'].append(dict(name = k, size = size, color = str(color[0])))
    else:
        for k, v in data.iteritems():
            cdata = buildChildStructure(k, v, sdata, color)
            if cdata['children']:
                child['children'].append(cdata)
    return child
            

def parseHierarchyYAML(filename, sampleid, sampledata):
    yml = yaml.load(open(filename))
    # structure takes the form of dictionary of dictionaries, in which the leaves are lists
    # we need a final format of {name: //Sample//, children: [ 
    #                                                          {name:##, children: [{name:#, size:@}, {name:#, size:@}}] },  
    #                                                          {name:##, children: [{name:#, size:@}, {name:#, size:@}}] }  ] }
    jsonformat = {}
    jsonformat['name'] = sampleid
    jsonformat['children'] = []
    jsonformat['color'] = "#3399FF"
    colormap = yml['colors']

    toplevelcolors = {}
    for k, v in yml.iteritems():
        if k == 'colors':
            continue
        cmap = colormap.get(k, colormap.get("default",["#000000"]*5) ) 
        cdata = buildChildStructure(k, v, sampledata, cmap)
        if cdata['children']:
            toplevelcolors[k] = cmap[0]
            jsonformat['children'].append(cdata)
    internal = []

    cmap = colormap.get("Internal Nodes", colormap.get("default",["#000000"]*5 ) )
    for name in  yml['Internal Nodes']:
        nm = name.split()[-1]
        nm = "%s_I:"%(nm)
        nm = nm.upper()
        size = 0
        for s, sd in sampledata.iteritems():
            if  s.upper().startswith(nm):
                size += int(sd)
                sampledata[s] = 0
        #size = sum([ int(sd) for s, sd in sampledata.iteritems() if s.upper().startswith(nm) ])
        if size:
            internal.append( dict(name = name, size = size, color = cmap[1]))

    if internal:
        toplevelcolors["Internal Nodes"] = cmap[0]
        cdata = dict(name = 'Internal Nodes', children = internal, color =cmap[0] )
        jsonformat['children'].append(cdata)

    cmap = colormap.get("default",["#000000"]*5)
    internal = []
    for s, sd in sampledata.iteritems():        
        if sd != 0:
            internal.append( dict(name = name, size = sd, color = cmap[1]))
    if internal:
        toplevelcolors["UNKNOWN"] = cmap[0]
        cdata = dict(name = 'UNKNOWN', children = internal, color = cmap[0] )
        jsonformat['children'].append(cdata)
    
    return json.dumps([jsonformat, toplevelcolors])


#a = [l.strip().split() for l in open(sys.argv[2])]
#ids = a[0][1:]
#data = dict(zip(ids, a[1][1:]))
#parseHierarchyYAML(sys.argv[1], a[1][0], data)
