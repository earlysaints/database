# GEDCOM to JSON-LD

In email conversations 2015-04-17, we discussed using JSON-LD as our shared data format.
Since I have a working knowlege of GEDCOM 5.5, and since Maurine Ward and Ron Watt's work is in GEDCOM format,
I decided to begin writing a GEDCOM to JSON-LD converter.
In doing so, I ran into a few problems, documented here.

## GEDCOM Identifiers are Blank Nodes

In GEDCOM, indentifers are scoped to an individual file and may change every single time the file is saved.
This makes them very similar to JSON-LD's blank nodes; I convert `@I123` into `_:I123`.

For creating a match databases, we'll need durable identifiers too.
Legacy Family Tree, the tool used by Ward and Watt, has durable unique identifiers in their `_UID` fields.
I do not know how widespread this practice is.

*Brandon: if the identifiers in GEDCOM are anything like the RIN in PAF, they tend to be durable (but yes, are only scoped within the file). However, that is probably up to the whim of whatever software created the file. I do not know what standard the Legacy UID comes from, but it is probably not a common practice among genealogy software. The EarlyLDS database only uses the GEDCOM I... identifiers.*

## Content and Nested Nodes

In GEDCOM, each element may have *both* some content (either text or a link)
*and* nested elements (or just one of the two, or neither).
In JSON-LD, a node may have one or the other but not both:
If a node has `@value`, it cannot also have non-`@` members.

We'll take as an example in this section the following GEDCOM snippet:

```
0 @I1@ INDI
1 NAME Stephen Joseph /Abbott/
2 GIVN Stephen Joseph
2 SURN Abbott
```

Some possible solutions:

### Double-depth

If a node has children and content, we insert a holder object to store them.

```
{ "@id": "_:I1"
, "@type": "INDI"
, "NAME":
  { "value": "Stephen Joseph /Abbott/"
  , "nested":
    { "GIVN": "Stephen Joseph"
    , "SURN": "Abbot"
    }
  }
}
```

### Payload field

We could use something like 
`http://schema.org/Property`, 
`http://schema.org/Text`,
`http://schema.org/URL`,
`http://www.w3.org/2000/01/rdf-schema#label`,
or another IRI of our own design to represent the payload.
Rather than pick one, I'll assume the `@context` defines aliases `$text` and `$link`.

```
{ "@id": "_:I1"
, "@type": "INDI"
, "NAME":
  { "$text": "Stephen Joseph /Abbott/"
  , "GIVN": "Stephen Joseph"
  , "SURN": "Abbot"
  }
}
```

I explored other options but found them both more verbose and less clear.

I'll use the payload field approach in my examples below.

*Brandon: This situation will come up quite often when we have a value with qualifiers, so we need to make sure we have a good generic solution; this requirement to associate a single content with a key is an inherent characteristic of all key-value/triple formats, including JSON and RDF, right? Your payload approach is almost identical to the most common way of handling this in RDF with a blank node. I don't like the fact that I have to take two hops to get to the value (which I have to do either way). The approach I've been working on, based on the quad/named graph idea in RDF (but not following it exactly), is to give every statement an identifier, so the qualifiers are pointing to the original statement by reference, not by nesting. For example, in pseudocode:*

```
25: @I1@ NAME "Stephen Joseph /Abbott/"
26: 25 GIVN "Stephen Joseph"
27: 25 SURN "Abbott"
```

*I have found it to be a clean way of handling a lot of complex situations. However, doing this in JSON-LD would be very unwieldy (every statement is an independent object), and would break the nested object model that makes JSON-LD nice to use.*

## `CONT` and `CONC` tags

GEDCOM has two nested tags, `CONT` and `CONC`, that are present only to allow text
to span multiple lines of the .ged file.
I am assuming these will be removed as a pre-processing step and not show up in the JSON-LD.

```
2 SOUR @S50@
3 PAGE M432, roll M432_919, p. 158, image 325, dwelling 155, famil
4 CONC y 155, Abigail Abbott household
3 QUAY 3
```

becomes

```
  , "SOUR" :
    { "$link": "_:S50"
    , "PAGE": "M432, roll M432_919, p. 158, image 325, dwelling 155, family 155, Abigail Abbott household"
    , "QUAY": 3
    }
```

## Normalization

I am not sure if we want to normalize data.
Some things we might want to normalize at some point:

* Are there family entities (as in GEDCOM) or links directly between parent/child?
* Do we standardize dates, names, places, etc., in some way?
* Do we allow free-form fields but have very descriptive `@type`s like `daterange#gregorian#start(YYYY)-end(YYYY-MM-DD)`?

I perform no normalization in the examples in this document.

*Brandon: As we discussed earlier, I think we start with minimal normalization (for the matching phase at least): let each database model the data the way it wants. The downside of that is that we have to be aware of 3-4 ways of representing a family, 3-4 ways of representing birth/death/etc. events. The alternative is that we have to decide a "correct" model to transform everything into, and frankly, after a long time of working on this, I'm not sure what that is. As for dates and places, I propose we don't normalize initially, but allow ourselves to do it later. We could either use different properties (placeText, placeURI, placeWKT, placeClean, etc.) or different types ("place": . . . @type: URI, etc.). Both have advantages and disadvantages. For standardized dates, I actually like the date format in GEDCOMX; it even handles uncertainty in a reasonable (if not 100% complete) way.*

## Multimaps

GEDCOM (and JSON, but not JSON-LD) has a multimap model; 
for example,

```
0 @F595@ FAM
1 HUSB @I2907@
1 WIFE @I2908@
1 MARR
1 CHIL @I671@
1 CHIL @I2909@
1 CHIL @I2944@
1 CHIL @I675@
```

has multiple `CHIL` fields.

I convert `MultiMap<K,V>` into `Map<K,Set<V>>`, as follows:

```
{ "@id": "_:F595"
, "@type": "FAM"
, "HUSB": "_:I2907"
, "WIFE": "_:I2908"
, "MARR": null
, "CHIL":
  [ "_:I671"
  , "_:I2909"
  , "_:I2944"
  , "_:I675"
  ]
}
```

## Larger Example

```
0 @I675@ INDI
1 NAME Phineas Howe /Young/
2 GIVN Phineas Howe
2 SURN Young
2 SOUR @S3@
1 SEX M
1 _UID E986FD790B444E2A8DDBF4B921A89B2449EB
1 CHAN
2 DATE 12 Mar 2010
3 TIME 21:28
1 FAMS @F594@
1 FAMC @F595@
0 @F595@ FAM
1 HUSB @I2907@
1 WIFE @I2908@
1 MARR
1 CHIL @I671@
1 CHIL @I2909@
1 CHIL @I2944@
1 CHIL @I675@
1 CHAN
2 DATE 12 Mar 2010
3 TIME 21:28
```

```
[ { "@id": "_:I675"
  , "@type": "INDI"
  , "NAME":
    { "$text": "Phineas Howe /Young/"
    , "GIVN": "Phineas Howe"
    , "SURN": Young"
    , "SOUR": "_:S3"
    }
  , "SEX": "M"
  , "_UID": "E986FD790B444E2A8DDBF4B921A89B2449EB"
  , "CHAN":
    { "DATE":
      { "$text": "12 Mar 2010"
      , "TIME": "21:28"
      }
    }
  , "FAMS": "_:F594"
  , "FAMC": "_:F595"
  }
, { "@id": "_:F595"
  , "@type": "FAM"
  , "HUSB": "_:I2907"
  , "WIFE": "_:I2908"
  , "MARR": null
  , "CHIL":
    [ "_:I671"
    , "_:I2909"
    , "_:I2944"
    , "_:I675"
    ]
  , "CHAN":
    { "DATE":
      { "$text": "12 Mar 2010"
      , "TIME": "21:28"
      }
    }
  }
]
```

* Brandon: I think this is a reasonable way to handle a many-to-many link. I think my quad approach above is better theoretically, but not in JSON-LD. One question; if I am trying to find this link from the child's perspective ("who are the parents of _:I671?"), how difficult will it be? I know it is a bit cumbersome when storing FK arrays in a ORDBMS. Personally, I believe that these kinds of "balanced" relationships (in which both nodes are of equal weight; it is not simply a property of one of them) should be stored independently of both of them, but the common practices of RDF, GEDCOMX, JSON-LD, etc. demonstrate that I am probably in the minority. *

## Context

To do: create a GEDCOM-appropriate `@context` object.

*Brandon: I get the feeling that it is best practice in JSON-LD to create a separate context for each incoming model that translates into universal URI's, right?*
