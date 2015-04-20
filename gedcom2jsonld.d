/**
 * See the accompanying gedcom2jsonld.md for the goal of this program.
 * 
 * Written in the D language version 2; see http://dlang.org for more.
 * 
 * An early prototype with little if any documentation and commenting.
 * Currently tailored to the LegacyFamilyTree flavor of GEDCOM 5.5.1 
 * in that it replaces «tab» with \t.
 * 
 * Currently does not output a @context, but should
 * 
 * Author: Luther Tychonievich
 * 
 * Licence: Released into the public domain
 */
module gedcom2jsonld;

import std.stdio : File;
import std.json : JSONValue, JSON_TYPE;

/// Tokenizer helper
string peekBit(string s) {
	import std.string : indexOf;
	auto index = s.indexOf(' ');
	if (index < 0) return s;
	return s[0..index];
}
/// Tokenizer helper
string popBit(ref string s) {
	import std.string : indexOf;
	auto index = s.indexOf(' ');
	if (index < 0) {
		string ans = s;
		s = null;
		return ans;
	} else {
		string ans = s[0..index];
		s = s[index+1..$];
		return ans;
	}
}

/// A GEDCOM "line": digit [id?] tag (link|content)
struct gedLine {
	int depth;
	string tag;
	string id;
	string xlink;
	string content;
	this(string line) {
		import std.conv : to;
		string d = line.popBit;
		if (d.length == 1) depth = d[0] - '0';
		else depth = to!int(d, 10);
		
		tag = line.popBit;
		if (tag[0] == '@' && tag[$-1] == '@') {
			id = tag[1..$-1];
			tag = line.popBit;
		}
		
		string link = line.peekBit;
		if (link.length > 0 && link[0] == '@' && link[$-1] == '@') {
			xlink = link[1..$-1];
			line.popBit;
		}
		
		content = line;
	}
	string toString() {
		string ans = "<"~tag;
		if (xlink) ans ~= " xlink:href=\"#"~xlink~"\"";
		if (id) ans ~= " id=\""~id~"\"";
		return ans ~ ">" ~ content;
	}
}

/// a GEDCOM "node" or "element": a line followed by 0 or more other lines with greater depth
struct gedNode {
	gedLine line;
	gedNode[] children;
	this(gedLine line) { this.line = line; }
	@property int depth() { return line.depth; }
	@property string tag() { return line.tag; }
	@property string id() { return line.id; }
	@property string xlink() { return line.xlink; }
	@property ref string content() { return line.content; }
}

/// a wrapper around the std.stdio File object to make them act like stacks of lines
struct bufFile {
	File readFrom;
	string[] buffer;
	this(ref File f) { this.readFrom = f; }
	this(string fname) { this.readFrom = File(fname); }
	string peek() {
		if (buffer.length > 0) {
			return buffer[$-1];
		} else if (readFrom.eof) {
			return null;
		} else {
			buffer ~= readFrom.readln();
			return buffer[$-1];
		}
	}
	string pop() {
		if (buffer.length > 0) {
			string ans = buffer[$-1];
			buffer.length = buffer.length - 1;
			return ans;
		}
		else if (readFrom.eof) return null;
		else {
			return readFrom.readln();
		}
	}
	void push(string line) {
		buffer ~= line;
	}
}

/// the main converter used in the code
JSONValue jsonld(gedNode n) 
in { 
	assert(n.depth == 0 || n.id == null, "assumption: no nested element has an ID"); 
	assert(n.xlink == null || n.content == null, "assumption: no element has both an xlink and content"); 
	assert(n.depth > 0 || n.xlink == null, "assumption: only nested elements have xlinks"); 
} body {
	import std.array : replace;
	JSONValue[string] ans;
	if (n.depth == 0) {
		ans["@type"] = JSONValue(n.tag);
		if (n.id) ans["@id"] = JSONValue("_:"~n.id);
		if (n.content) ans["$txt"] = JSONValue(n.content.replace("«tab»", "\t")); // HACK for LegacyFT
	} else {
		if (n.xlink && !n.children) return JSONValue("_:"~n.xlink);
		if (n.content && !n.children) return JSONValue(n.content.replace("«tab»", "\t")); // HACK for LegacyFT
		if (n.xlink) ans["$lnk"] = JSONValue("_:"~n.xlink);
		if (n.content) ans["$txt"] = JSONValue(n.content.replace("«tab»", "\t")); // HACK for LegacyFT
	}
	foreach(child; n.children) {
		if (child.tag in ans) {
			if (ans[child.tag].type == JSON_TYPE.ARRAY) {
			} else {
				ans[child.tag] = JSONValue([ans[child.tag], jsonld(child)]);
			}
		} else {
			ans[child.tag] = jsonld(child);
		}
	}
	return JSONValue(ans);
}

/// my preferred way of formatting json, with alphabetical key orderings
/// Currently does *not* enforce @set vs @list
string canonicalString(JSONValue obj, string leader="", bool newline=false) {
	import std.algorithm : sort;
	if (obj.type == JSON_TYPE.OBJECT) {
		string[] keys = obj.object.keys;
		string ans;
		if (newline && keys.length > 0) ans ~= "\n" ~ leader;
		ans ~= "{ ";

		sort(keys);
		foreach(i,k; keys) {
			if (i > 0) ans ~= ", ";
			ans ~= JSONValue(k).toString;
			ans ~= ": ";
			ans ~= canonicalString(obj[k], leader~"  ", true);
			ans ~= "\n"~leader;
		}

		ans ~= "}";
		return ans;
	} else if (obj.type == JSON_TYPE.ARRAY) {
		JSONValue[] raw = obj.array;
		string ans;
		if (newline && raw.length > 0) ans ~= "\n" ~ leader;
		ans ~= "[ ";

		string[] vals = new string[raw.length];
		foreach(i,v; raw) vals[i] = canonicalString(v, leader~"  ", false);
		vals.sort();
		foreach(i,v; vals) {
			if (i > 0) ans ~= ", ";
			ans ~= v;
			ans ~= "\n"~leader;
		}
		ans ~= "]";
		return ans;
	} else {
		return obj.toString;
	}
}


void main(string[] args) {
	import std.string : strip;
	import std.container.slist : SList;
	import std.array : Appender;
	import std.stdio : write, writeln;

	if (args.length == 1) {
		writeln("USAGE: ",args[0]," somefile.ged > somefile.jsonld");
	}
	string BOM = "\uFEFF";
	foreach(arg; args[1..$]) {
		
		Appender!(gedNode[]) level0;
		SList!gedNode stack;

		gedLine gl;// = "0 gedcom55";
		auto s = bufFile(arg);
		string line;
		
		
		// step 1: build up the data, handling CONT and CONC tags as we go
		while((line = s.pop) != null) {
			if (line[0..BOM.length] == BOM) line = line[BOM.length..$];
			gl = gedLine(line.strip());
			
			if (gl.tag == "CONT") {
				stack.front.content ~= "\n"~gl.content;
			} else if (gl.tag == "CONC") {
				stack.front.content ~= gl.content;
			} else {
				while (!stack.empty && stack.front.depth >= gl.depth) {
					auto old = stack.front;
					stack.removeFront;
					if (stack.empty) {
						level0 ~= old;
					} else {
						stack.front.children ~= old;
					}
				}
				stack.insertFront(gedNode(gl));
			}
		}
		while (!stack.empty) {
			auto old = stack.front;
			stack.removeFront;
			if (stack.empty) {
				level0 ~= old;
			} else {
				stack.front.children ~= old;
			}
		}
		gedNode[] master = level0.data;
		
		// step 2: convert top-level to JSONValue object, one at a time
		write("{ \"@graph\": \n  [ ");
		foreach(i,gl0; master) {
			if (i > 0) write("  , ");
			writeln(canonicalString(jsonld(gl0),"    ",false));
		}
		writeln("  ]\n}");
		
		// TODO: handle «/?[uib]», «/?sup»
	}
}

