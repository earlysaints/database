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

## Context

To do: create a GEDCOM-appropriate `@context` object.
