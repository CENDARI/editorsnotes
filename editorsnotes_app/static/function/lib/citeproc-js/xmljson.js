/*
 * Copyright (c) 2009-2013 Frank G. Bennett, Jr. All Rights
 * Reserved.
 *
 * The contents of this file are subject to the Common Public
 * Attribution License Version 1.0 (the “License”); you may not use
 * this file except in compliance with the License. You may obtain a
 * copy of the License at:
 *
 * http://bitbucket.org/fbennett/citeproc-js/src/tip/LICENSE.
 *
 * The License is based on the Mozilla Public License Version 1.1 but
 * Sections 1.13, 14 and 15 have been added to cover use of software over a
 * computer network and provide for limited attribution for the
 * Original Developer. In addition, Exhibit A has been modified to be
 * consistent with Exhibit B.
 *
 * Software distributed under the License is distributed on an “AS IS”
 * basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
 * the License for the specific language governing rights and limitations
 * under the License.
 *
 * The Original Code is the citation formatting software known as
 * "citeproc-js" (an implementation of the Citation Style Language
 * [CSL]), including the original test fixtures and software located
 * under the ./tests subdirectory of the distribution archive.
 *
 * The Original Developer is not the Initial Developer and is
 * __________. If left blank, the Original Developer is the Initial
 * Developer.
 *
 * The Initial Developer of the Original Code is Frank G. Bennett,
 * Jr. All portions of the code written by Frank G. Bennett, Jr. are
 * Copyright (c) 2009-2013 Frank G. Bennett, Jr. All Rights Reserved.
 *
 * Alternatively, the contents of this file may be used under the
 * terms of the GNU Affero General Public License (the [AGPLv3]
 * License), in which case the provisions of [AGPLv3] License are
 * applicable instead of those above. If you wish to allow use of your
 * version of this file only under the terms of the [AGPLv3] License
 * and not to allow others to use your version of this file under the
 * CPAL, indicate your decision by deleting the provisions above and
 * replace them with the notice and other provisions required by the
 * [AGPLv3] License. If you do not delete the provisions above, a
 * recipient may use your version of this file under either the CPAL
 * or the [AGPLv3] License.”
 */

/**
 * Functions for parsing an XML object converted to JSON.
 */

/*
  Style and locale JSON should be formatted as follows. Note that
  an empty literal should be set as an explicit empty strings within
  children:[]
  
  {
    name:"term",
    children:[
      ""
    ],
    attrs:{
      name:"author"
    }
  }

  The following script will generate correctly formatted JSON
  from a CSL style or locale file:

#!/usr/bin/python
''' Make me a module
'''

from xml.dom import minidom
import json,re

class jsonwalker:
    
    def __init__(self):
        pass

    def makedoc(self,xmlstring):
        #xmlstring = re.sub("(?ms)^<\?[^>]*\?>","",xmlstring);
        dom = minidom.parseString(xmlstring)
        return dom.documentElement

    def walktojson(self, elem):
        obj = {}
        obj["name"] = elem.nodeName
        obj["attrs"] = {}
        if elem.attributes:
            for key in elem.attributes.keys():
                obj["attrs"][key] = elem.attributes[key].value
        obj["children"] = []
        if len(elem.childNodes) == 0 and elem.nodeName == "term":
            obj["children"] = [""]
        for child in elem.childNodes:
            if child.nodeName == "#comment":
                pass
            elif child.nodeName == "#text":
                if len(elem.childNodes) == 1 and elem.nodeName in ["term","single","multiple"]:
                    obj["children"].append(child.wholeText)
            else:
                obj["children"].append(self.walktojson(child))
        return obj

if __name__ == "__main__":

    import sys
    w = jsonwalker()
    doc = w.makedoc(open(sys.argv[1]).read())
    obj = w.walktojson(doc)
    print json.dumps(obj,indent=2)

*/

// Don't clobber an existing value if this has already been declared.
if ("undefined" === typeof CSL_IS_IE) {
    var CSL_IS_IE;
};

var CSL_JSON = function () {
    this.institution = {
        name:"institution",
        attrs:{
            "institution-parts":"long",
            "delimiter":", ",
            "substitute-use-first":"1",
            "use-last":"1"
        },
        children:[
            {
                name:"institution-part",
                attrs:{
                    name:"long"
                },
                children:[]
            }
        ]
    };
};

/**
 * No need for cleaning with native JSON.
 */
CSL_JSON.prototype.clean = function (json) {
    return json;
};


/**
 * Methods to call on a node.
 */
CSL_JSON.prototype.getStyleId = function (myjson) {
    return myjson.attrs.id;
};

CSL_JSON.prototype.children = function (myjson) {
    //print("children()");
    if (myjson && myjson.children.length) {
        return myjson.children.slice();
    } else {
        return false;
    }
};

CSL_JSON.prototype.nodename = function (myjson) {
    //print("nodename()");
    return myjson.name;
};

CSL_JSON.prototype.attributes = function (myjson) {
    //print("attributes()");
    var ret = {};
    for (var attrname in myjson.attrs) {
        ret["@"+attrname] = myjson.attrs[attrname];
    }
    return ret;
};


CSL_JSON.prototype.content = function (myjson) {
    //print("content()");
    // xmldom.js and xmle4x.js have "undefined" as default
    var ret = "";
    // This only catches content at first level, but that is good enough
    // for us.
    if (!myjson || !myjson.children) {
        return ret;
    }
    for (var i=0, ilen=myjson.children.length; i < ilen; i += 1) {
        if ("string" === typeof myjson.children[i]) {
            ret += myjson.children[i];
        }
    }
    return ret;
};


CSL_JSON.prototype.namespace = {}

CSL_JSON.prototype.numberofnodes = function (myjson) {
    //print("numberofnodes()");
    if (myjson && "number" == typeof myjson.length) {
        return myjson.length;
    } else {
        return 0;
    }
};

// getAttributeName() removed. Looks like it was not being used.

CSL_JSON.prototype.getAttributeValue = function (myjson,name,namespace) {
    //print("getAttributeValue()");
    var ret = "";
    if (namespace) {
        name = namespace+":"+name;
    }
    if (myjson) {
        if (myjson.attrs) {
            if (myjson.attrs[name]) {
                ret = myjson.attrs[name];
            } else {
                ret = "";
            }
        }
    }
    return ret;
}

CSL_JSON.prototype.getNodeValue = function (myjson,name) {
    //print("getNodeValue()");
    var ret = "";
    if (name){
        for (var i=0, ilen=myjson.children.length; i < ilen; i += 1) {
            if (myjson.children[i].name === name) {
                // This will always be Object() unless empty
                if (myjson.children[i].children.length) {
                    ret = myjson.children[i];
                } else {
                    ret = "";
                }
            }
        }
    } else if (myjson) {
        ret = myjson;
    }
    // Just being careful here, following the former DOM code. The JSON object we receive 
    // for this should be fully normalized.
    if (ret && ret.children && ret.children.length == 1 && "string" === typeof ret.children[0]) {
        ret = ret.children[0];
    }
    return ret;
}

CSL_JSON.prototype.setAttributeOnNodeIdentifiedByNameAttribute = function (myjson,nodename,partname,attrname,val) {
    //print("setAttributeOnNodeIdentifiedByNameAttribute()");
    var pos, len, xml, nodes, node;
    if (attrname.slice(0,1) === '@'){
        attrname = attrname.slice(1);
    }
    // In the one place this is used in citeproc-js code, it doesn't need to recurse.
    for (var i=0,ilen=myjson.children.length; i<ilen; i += 1) {
        if (myjson.children[i].name === nodename && myjson.children[i].attrs.name === partname) {
            myjson.children[i].attrs[attrname] = val;
        }
    }
}

CSL_JSON.prototype.deleteNodeByNameAttribute = function (myjson,val) {
    //print("deleteNodeByNameAttribute()");
    var i, ilen;
    for (i = 0, ilen = myjson.children.length; i < ilen; i += 1) {
        if (!myjson.children[i] || "string" === typeof myjson.children[i]) {
            continue;
        }
        if (myjson.children[i].attrs.name == val) {
            myjson.children = myjson.children.slice(0,i).concat(myjson.children.slice(i+1));
        }
    }
}

CSL_JSON.prototype.deleteAttribute = function (myjson,attrname) {
    //print("deleteAttribute()");
    var i, ilen;
    if ("undefined" !== typeof myjson.attrs[attrname]) {
        myjson.attrs.pop(attrname);
    }
}

CSL_JSON.prototype.setAttribute = function (myjson,attr,val) {
    //print("setAttribute()");
    myjson.attrs[attr] = val;
    return false;
}

CSL_JSON.prototype.nodeCopy = function (myjson,clone) {
    //print("nodeCopy()");
    if (!clone) {
        var clone = {};
    }
    if ("object" === typeof clone && "undefined" === typeof clone.length) {
        // myjson is an object
        for (var key in myjson) {
            if ("string" === typeof myjson[key]) {
                clone[key] = myjson[key];
            } else if ("object" === typeof myjson[key]) {
                if ("undefined" === typeof myjson[key].length) {
                    clone[key] = this.nodeCopy(myjson[key],{});
                } else {
                    clone[key] = this.nodeCopy(myjson[key],[]);
                }
            }
        }
    } else {
        // myjson is an array
        for (var i=0,ilen=myjson.length;i<ilen; i += 1) {
            if ("string" === typeof myjson[i]) {
                clone[i] = myjson[i];
            } else {
                // If it's at the first level of an array, it's an object.
                clone[i] = this.nodeCopy(myjson[i],{});
            }
        }
    }
    return clone;
}

CSL_JSON.prototype.getNodesByName = function (myjson,name,nameattrval,ret) {
    //print("getNodesByName()");
    var nodes, node, pos, len;
    if (!ret) {
        var ret = [];
    }
    if (!myjson || !myjson.children) {
        return ret;
    }
    if (name === myjson.name) {
        if (nameattrval) {
            if (nameattrval === myjson.attrs.name) {
                ret.push(myjson);
            }
        } else {
            ret.push(myjson);
        }
    }
    for (var i=0,ilen=myjson.children.length;i<ilen;i+=1){
        if ("object" !== typeof myjson.children[i]) {
            continue;
        }
        this.getNodesByName(myjson.children[i],name,nameattrval,ret);
    }
    return ret;
}

CSL_JSON.prototype.nodeNameIs = function (myjson,name) {
    //print("nodeNameIs()");
    if (name == myjson.name) {
        return true;
    }
    return false;
}

CSL_JSON.prototype.makeXml = function (myjson) {
    //print("makeXml()");
    return myjson;
};

CSL_JSON.prototype.insertChildNodeAfter = function (parent,node,pos,datejson) {
    //print("insertChildNodeAfter()");
    // Function is misnamed: this replaces the node
    for (var i=0,ilen=parent.children.length;i<ilen;i+=1) {
        if (node === parent.children[i]) {
            parent.children = parent.children.slice(0,i).concat([datejson]).concat(parent.children.slice(i+1));
            break;
        }
    }
    return parent;
};


CSL_JSON.prototype.insertPublisherAndPlace = function(myjson) {
    if (myjson.name === "group") {
        var useme = true;
        var mustHaves = ["publisher","publisher-place"];
        for (var i=0,ilen=myjson.children.length;i<ilen;i+=1) {
            var haveVarname = mustHaves.indexOf(myjson.children[i].attrs.variable);
            var isText = myjson.children[i].name === "text";
            if (isText && haveVarname > -1 && !myjson.children[i].attrs.prefix && !myjson.children[i].attrs.suffix) {
                mustHaves = mustHaves.slice(0,haveVarname).concat(mustHaves.slice(haveVarname+1));
            } else {
                useme = false;
                break;
            }
        }
        if (useme && !mustHaves.length) {
            myjson.attrs["has-publisher-and-publisher-place"] = true;
       }
    }
    for (var i=0,ilen=myjson.children.length;i<ilen;i+=1) {
        if ("object" === typeof myjson.children[i]) {
            this.insertPublisherAndPlace(myjson.children[i]);
        }
    }    
}
/*
CSL_JSON.prototype.insertPublisherAndPlace = function(myxml) {
    var group = myxml.getElementsByTagName("group");
    for (var i = 0, ilen = group.length; i < ilen; i += 1) {
        var node = group.item(i);
        var skippers = [];
        for (var j = 0, jlen = node.childNodes.length; j < jlen; j += 1) {
            if (node.childNodes.item(j).nodeType !== 1) {
                skippers.push(j);
            }
        }
        if (node.childNodes.length - skippers.length === 2) {
            var twovars = [];
            for (var j = 0, jlen = 2; j < jlen; j += 1) {
                if (skippers.indexOf(j) > -1) {
                    continue;
                }
                var child = node.childNodes.item(j);                    
                var subskippers = [];
                for (var k = 0, klen = child.childNodes.length; k < klen; k += 1) {
                    if (child.childNodes.item(k).nodeType !== 1) {
                        subskippers.push(k);
                    }
                }
                if (child.childNodes.length - subskippers.length === 0) {
                    twovars.push(child.getAttribute('variable'));
                    if (child.getAttribute('suffix')
                        || child.getAttribute('prefix')) {
                        twovars = [];
                        break;
                    }
                }
            }
            if (twovars.indexOf("publisher") > -1 && twovars.indexOf("publisher-place") > -1) {
                node.setAttribute('has-publisher-and-publisher-place', true);
            }
        }
    }
};
*/

CSL_JSON.prototype.addMissingNameNodes = function(myjson,parentname) {
    //print("addMissingNameNodes()");
    if (myjson.name === "names") {
        if (myjson.children.length === 0 && "substitute" !== parentname) {
             myjson.children.push({name:"name",attrs:{},children:[]})
        }
    }
    for (var i=0,ilen=myjson.children.length;i<ilen;i+=1) {
        if ("object" === typeof myjson.children[i]) {
            this.addMissingNameNodes(myjson.children[i],myjson.name);
        }
    }
}

CSL_JSON.prototype.addInstitutionNodes = function(myjson) {
    //print("addInstitutionNodes()");
    var names, thenames, institution, theinstitution, name, thename, xml, pos, len;
    // The idea here is to map relevant attributes from name and nampart=family
    // to the "long" institution-part node, when and only when forcing insert
    // of the default node.
    if (myjson.name === "names") {
        // do stuff
        var attributes = {};
        var insertPos = -1;
        for (var i=0,ilen=myjson.children.length;i<ilen;i+=1) {
            if (myjson.children[i].name == "name") {
                for (var key in myjson.children[i].attrs) {
                    attributes[key] = myjson.children[i].attrs[key];
                }
                attributes.delimiter = myjson.children[i].attrs.delimiter;
                attributes.and = myjson.children[i].attrs.and;
                insertPos = i;
                for (var k=0,klen=myjson.children[i].children.length;k<klen;k+=1) {
                    if (myjson.children[i].children[k].attrs.name !== 'family') {
                        continue;
                    }
                    for (var key in myjson.children[i].children[k].attrs) {
                        attributes[key] = myjson.children[i].children[k].attrs[key];
                    }
                }
            }
            if (myjson.children[i].name == "institution") {
                insertPos = -1;
                break;
            }
        }
        if (insertPos > -1) {
            var institution = this.nodeCopy(this.institution);
            for (var i=0,ilen = CSL.INSTITUTION_KEYS.length;i<ilen;i+=1) {
                var attrname = CSL.INSTITUTION_KEYS[i];
                if ("undefined" !== typeof attributes[attrname]) {
                    institution.children[0].attrs[attrname] = attributes[attrname];
                }
                if (attributes.delimiter) {
                    institution.attrs.delimiter = attributes.delimiter;
                }
                if (attributes.and) {
                    institution.attrs.and = "text";
                }
            }
            myjson.children = myjson.children.slice(0,insertPos+1).concat([institution]).concat(myjson.children.slice(insertPos+1));
        }
    }
    for (var i=0,ilen=myjson.children.length;i<ilen;i+=1) {
        if ("string" === typeof myjson.children[i]) {
            continue;
        }
        // Recurse
        this.addInstitutionNodes(myjson.children[i]);
    }
}
CSL_JSON.prototype.flagDateMacros = function(myjson) {
    //print("flagDateMacros()");
    for (var i=0,ilen=myjson.children.length;i<ilen;i+=1) {
        if (myjson.children[i].name === "macro") {
            if (this.inspectDateMacros(myjson.children[i])) {
                myjson.children[i].attrs["macro-has-date"] = "true";
            }
        }
    }
}
CSL_JSON.prototype.inspectDateMacros = function(myjson) {
    //print("inspectDateMacros()");
    if (!myjson || !myjson.children) {
        return false;
    }
    if (myjson.name === "date") {
        return true;
    } else {
        for (var i=0,ilen=myjson.children.length;i<ilen;i+=1) {
            if (this.inspectDateMacros(myjson.children[i])) {
                return true;
            }
        }
    }
    return false;
}
