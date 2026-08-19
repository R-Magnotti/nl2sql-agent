legal_fns = '''
BIGQUERY (GOOGLESQL) FUNCTION REFERENCE
=======================================

This topic contains all functions supported by GoogleSQL for BigQuery.

408 functions

ABS                                     Computes the absolute value of X.
ACOS                                    Computes the inverse cosine of X.
ACOSH                                   Computes the inverse hyperbolic cosine of X.
AEAD.DECRYPT_BYTES                      Uses the matching key from a keyset to decrypt a BYTES ciphertext.
AEAD.DECRYPT_STRING                     Uses the matching key from a keyset to decrypt a BYTES ciphertext into a STRING plaintext.
AEAD.ENCRYPT                            Encrypts STRING plaintext, using the primary cryptographic key in a keyset.
AGG                                     Aggregates a measure type.
ANY_VALUE                               Gets an expression for some row.
APPENDS                                 Returns all rows appended to a table for a given time range.
APPROX_COUNT_DISTINCT                   Gets the approximate result for COUNT(DISTINCT expression).
APPROX_QUANTILES                        Gets the approximate quantile boundaries.
APPROX_TOP_COUNT                        Gets the approximate top elements and their approximate count.
APPROX_TOP_SUM                          Gets the approximate top elements and sum, based on the approximate sum of an assigned weight.
ARRAY                                   Produces an array with one element for each row in a subquery.
ARRAY_AGG                               Gets an array of values.
ARRAY_CONCAT                            Concatenates one or more arrays with the same element type into a single array.
ARRAY_CONCAT_AGG                        Concatenates arrays and returns a single array as a result.
ARRAY_FIRST                             Gets the first element in an array.
ARRAY_LAST                              Gets the last element in an array.
ARRAY_LENGTH                            Gets the number of elements in an array.
ARRAY_REVERSE                           Reverses the order of elements in an array.
ARRAY_SLICE                             Produces an array containing zero or more consecutive elements from an input array.
ARRAY_TO_STRING                         Produces a concatenation of the elements in an array as a STRING value.
ASCII                                   Gets the ASCII code for the first character or byte in a STRING or BYTES value.
ASIN                                    Computes the inverse sine of X.
ASINH                                   Computes the inverse hyperbolic sine of X.
ATAN                                    Computes the inverse tangent of X.
ATAN2                                   Computes the inverse tangent of X/Y, using the signs of X and Y to determine the quadrant.
ATANH                                   Computes the inverse hyperbolic tangent of X.
AVG                                     Gets the average of non-NULL values.
AVG (Differential Privacy)              DIFFERENTIAL_PRIVACY-supported AVG. Gets the differentially-private average of non-NULL, non-NaN values in a query with a DIFFERENTIAL_PRIVACY clause.
BAG_OF_WORDS                            Gets the frequency of each term (token) in a tokenized document.
BIT_AND                                 Performs a bitwise AND operation on an expression.
BIT_COUNT                               Gets the number of bits that are set in an input expression.
BIT_OR                                  Performs a bitwise OR operation on an expression.
BIT_XOR                                 Performs a bitwise XOR operation on an expression.
BOOL                                    Converts a JSON boolean to a SQL BOOL value.
BYTE_LENGTH                             Gets the number of BYTES in a STRING or BYTES value.
CAST                                    Convert the results of an expression to the given type.
CBRT                                    Computes the cube root of X.
CEIL                                    Gets the smallest integral value that isn't less than X.
CEILING                                 Synonym of CEIL.
CHANGES                                 Returns all rows that have changed in a table for a given time range.
CHAR_LENGTH                             Gets the number of characters in a STRING value.
CHARACTER_LENGTH                        Synonym for CHAR_LENGTH.
CHR                                     Converts a Unicode code point to a character.
CODE_POINTS_TO_BYTES                    Converts an array of extended ASCII code points to a BYTES value.
CODE_POINTS_TO_STRING                   Converts an array of extended ASCII code points to a STRING value.
COLLATE                                 Combines a STRING value and a collation specification into a collation specification-supported STRING value.
CONCAT                                  Concatenates one or more STRING or BYTES values into a single result.
CONTAINS_SUBSTR                         Performs a normalized, case-insensitive search to see if a value exists as a substring in an expression.
CORR                                    Computes the Pearson coefficient of correlation of a set of number pairs.
COS                                     Computes the cosine of X.
COSH                                    Computes the hyperbolic cosine of X.
COSINE_DISTANCE                         Computes the cosine distance between two vectors.
COT                                     Computes the cotangent of X.
COTH                                    Computes the hyperbolic cotangent of X.
COUNT                                   Gets the number of rows in the input, or the number of rows with an expression evaluated to any value other than NULL.
COUNT (Differential Privacy)            DIFFERENTIAL_PRIVACY-supported COUNT. Signature 1: Gets the differentially-private count of rows in a query with a DIFFERENTIAL_PRIVACY clause. Signature 2: Gets the differentially-private count of rows with a non-NULL expression in a query with a DIFFERENTIAL_PRIVACY clause.
COUNTIF                                 Gets the number of TRUE values for an expression.
COVAR_POP                               Computes the population covariance of a set of number pairs.
COVAR_SAMP                              Computes the sample covariance of a set of number pairs.
CSC                                     Computes the cosecant of X.
CSCH                                    Computes the hyperbolic cosecant of X.
CUME_DIST                               Gets the cumulative distribution (relative position (0,1\]) of each row within a window.
CURRENT_DATE                            Returns the current date as a DATE value.
CURRENT_DATETIME                        Returns the current date and time as a DATETIME value.
CURRENT_TIME                            Returns the current time as a TIME value.
CURRENT_TIMESTAMP                       Returns the current date and time as a TIMESTAMP object.
DATE                                    Constructs a DATE value.
DATE_ADD                                Adds a specified time interval to a DATE value.
DATE_BUCKET                             Gets the lower bound of the date bucket that contains a date.
DATE_DIFF                               Gets the number of unit boundaries between two DATE values at a particular time granularity.
DATE_FROM_UNIX_DATE                     Interprets an INT64 expression as the number of days since 1970-01-01.
DATE_SUB                                Subtracts a specified time interval from a DATE value.
DATE_TRUNC                              Truncates a DATE, DATETIME, or TIMESTAMP value at a particular granularity.
DATETIME                                Constructs a DATETIME value.
DATETIME_ADD                            Adds a specified time interval to a DATETIME value.
DATETIME_BUCKET                         Gets the lower bound of the datetime bucket that contains a datetime.
DATETIME_DIFF                           Gets the number of unit boundaries between two DATETIME values at a particular time granularity.
DATETIME_SUB                            Subtracts a specified time interval from a DATETIME value.
DATETIME_TRUNC                          Truncates a DATETIME or TIMESTAMP value at a particular granularity.
DENSE_RANK                              Gets the dense rank (1-based, no gaps) of each row within a window.
DESTINATION_NODE_ID                     Gets a unique identifier of a graph edge's destination node.
DETERMINISTIC_DECRYPT_BYTES             Uses the matching key from a keyset to decrypt a BYTES ciphertext, using deterministic AEAD.
DETERMINISTIC_DECRYPT_STRING            Uses the matching key from a keyset to decrypt a BYTES ciphertext into a STRING plaintext, using deterministic AEAD.
DETERMINISTIC_ENCRYPT                   Encrypts STRING plaintext, using the primary cryptographic key in a keyset, using deterministic AEAD encryption.
DIV                                     Divides integer X by integer Y.
DLP_DETERMINISTIC_ENCRYPT               Encrypts data with a DLP compatible algorithm.
DLP_DETERMINISTIC_DECRYPT               Decrypts DLP-encrypted data.
DLP_KEY_CHAIN                           Gets a data encryption key that's wrapped by Cloud Key Management Service.
FLOAT64                                 Converts a JSON number to a SQL FLOAT64 value.
EDGES                                   Gets the edges in a graph path. The resulting array retains the original order in the graph path.
EDIT_DISTANCE                           Computes the Levenshtein distance between two STRING or BYTES values.
ELEMENT_ID                              Gets a graph element's unique identifier.
ENDS_WITH                               Checks if a STRING or BYTES value is the suffix of another value.
ERROR                                   Produces an error with a custom error message.
EXP                                     Computes e to the power of X.
EXTERNAL_OBJECT_TRANSFORM               Produces an object table with the original columns plus one or more additional columns.
EXTERNAL_QUERY                          Executes a query on an external database and returns the results as a temporary table.
EXTRACT                                 Extracts part of a date from a DATE value.
EXTRACT                                 Extracts part of a date and time from a DATETIME value.
EXTRACT                                 Extracts part of an INTERVAL value.
EXTRACT                                 Extracts part of a TIME value.
EXTRACT                                 Extracts part of a TIMESTAMP value.
EUCLIDEAN_DISTANCE                      Computes the Euclidean distance between two vectors.
FARM_FINGERPRINT                        Computes the fingerprint of a STRING or BYTES value, using the FarmHash Fingerprint64 algorithm.
FIRST_VALUE                             Gets a value for the first row in the current window frame.
FLOOR                                   Gets the largest integral value that isn't greater than X.
FORMAT_DATE                             Formats a DATE value according to a specified format string.
FORMAT_DATETIME                         Formats a DATETIME value according to a specified format string.
FORMAT_TIME                             Formats a TIME value according to the specified format string.
FORMAT_TIMESTAMP                        Formats a TIMESTAMP value according to the specified format string.
FORMAT                                  Formats data and produces the results as a STRING value.
FROM_BASE32                             Converts a base32-encoded STRING value into a BYTES value.
FROM_BASE64                             Converts a base64-encoded STRING value into a BYTES value.
FROM_HEX                                Converts a hexadecimal-encoded STRING value into a BYTES value.
GAP_FILL                                Finds and fills gaps in a time series.
GENERATE_ARRAY                          Generates an array of values in a range.
GENERATE_DATE_ARRAY                     Generates an array of dates in a range.
GENERATE_RANGE_ARRAY                    Splits a range into an array of subranges.
GENERATE_TIMESTAMP_ARRAY                Generates an array of timestamps in a range.
GENERATE_UUID                           Produces a random universally unique identifier (UUID) as a STRING value.
GREATEST                                Gets the greatest value among X1,...,XN.
GROUPING                                Checks if a groupable value in the GROUP BY clause is aggregated.
HLL_COUNT.EXTRACT                       Extracts a cardinality estimate of an HLL++ sketch.
HLL_COUNT.INIT                          Aggregates values of the same underlying type into a new HLL++ sketch.
HLL_COUNT.MERGE                         Merges HLL++ sketches of the same underlying type into a new sketch, and then gets the cardinality of the new sketch.
HLL_COUNT.MERGE_PARTIAL                 Merges HLL++ sketches of the same underlying type into a new sketch.
IEEE_DIVIDE                             Divides X by Y, but doesn't generate errors for division by zero or overflow.
INITCAP                                 Formats a STRING as proper case, which means that the first character in each word is uppercase and all other characters are lowercase.
INSTR                                   Finds the position of a subvalue inside another value, optionally starting the search at a given offset or occurrence.
INT64                                   Converts a JSON number to a SQL INT64 value.
IS_INF                                  Checks if X is positive or negative infinity.
IS_NAN                                  Checks if X is a NaN value.
JSON_ARRAY                              Creates a JSON array.
JSON_ARRAY_APPEND                       Appends JSON data to the end of a JSON array.
JSON_ARRAY_INSERT                       Inserts JSON data into a JSON array.
JSON_EXTRACT                            (Deprecated) Extracts a JSON value and converts it to a SQL JSON-formatted STRING or JSON value.
JSON_EXTRACT_ARRAY                      (Deprecated) Extracts a JSON array and converts it to a SQL ARRAY<JSON-formatted STRING> or ARRAY<JSON> value.
JSON_EXTRACT_SCALAR                     (Deprecated) Extracts a JSON scalar value and converts it to a SQL STRING value.
JSON_EXTRACT_STRING_ARRAY               (Deprecated) Extracts a JSON array of scalar values and converts it to a SQL ARRAY<STRING> value.
JSON_FLATTEN                            Produces a new SQL ARRAY<JSON> value containing all non-array values that are either directly in the input JSON value or children of one or more consecutively nested arrays in the input JSON value.
JSON_KEYS                               Extracts unique JSON keys from a JSON expression.
JSON_OBJECT                             Creates a JSON object.
JSON_QUERY                              Extracts a JSON value and converts it to a SQL JSON-formatted STRING or JSON value.
JSON_QUERY_ARRAY                        Extracts a JSON array and converts it to a SQL ARRAY<JSON-formatted STRING> or ARRAY<JSON> value.
JSON_REMOVE                             Produces JSON with the specified JSON data removed.
JSON_SET                                Inserts or replaces JSON data.
JSON_STRIP_NULLS                        Removes JSON nulls from JSON objects and JSON arrays.
JSON_TYPE                               Gets the JSON type of the outermost JSON value and converts the name of this type to a SQL STRING value.
JSON_VALUE                              Extracts a JSON scalar value and converts it to a SQL STRING value.
JSON_VALUE_ARRAY                        Extracts a JSON array of scalar values and converts it to a SQL ARRAY<STRING> value.
JUSTIFY_DAYS                            Normalizes the day part of an INTERVAL value.
JUSTIFY_HOURS                           Normalizes the time part of an INTERVAL value.
JUSTIFY_INTERVAL                        Normalizes the day and time parts of an INTERVAL value.
KEYS.ADD_KEY_FROM_RAW_BYTES             Adds a key to a keyset, and return the new keyset as a serialized BYTES value.
KEYS.KEYSET_CHAIN                       Produces a Tink keyset that's encrypted with a Cloud KMS key.
KEYS.KEYSET_FROM_JSON                   Converts a STRING JSON keyset to a serialized BYTES value.
KEYS.KEYSET_LENGTH                      Gets the number of keys in the provided keyset.
KEYS.KEYSET_TO_JSON                     Gets a JSON STRING representation of a keyset.
KEYS.NEW_KEYSET                         Gets a serialized keyset containing a new key based on the key type.
KEYS.NEW_WRAPPED_KEYSET                 Creates a new keyset and encrypts it with a Cloud KMS key.
KEYS.REWRAP_KEYSET                      Re-encrypts a wrapped keyset with a new Cloud KMS key.
KEYS.ROTATE_KEYSET                      Adds a new primary cryptographic key to a keyset, based on the key type.
KEYS.ROTATE_WRAPPED_KEYSET              Rewraps a keyset and rotates it.
KLL_QUANTILES.EXTRACT_INT64             Gets a selected number of quantiles from an INT64-initialized KLL sketch.
KLL_QUANTILES.EXTRACT_FLOAT64           Gets a selected number of quantiles from a FLOAT64-initialized KLL sketch.
KLL_QUANTILES.EXTRACT_POINT_INT64       Gets a specific quantile from an INT64-initialized KLL sketch.
KLL_QUANTILES.EXTRACT_POINT_FLOAT64     Gets a specific quantile from a FLOAT64-initialized KLL sketch.
KLL_QUANTILES.INIT_INT64                Aggregates values into an INT64-initialized KLL sketch.
KLL_QUANTILES.INIT_FLOAT64              Aggregates values into a FLOAT64-initialized KLL sketch.
KLL_QUANTILES.MERGE_INT64               Merges INT64-initialized KLL sketches into a new sketch, and then gets the quantiles from the new sketch.
KLL_QUANTILES.MERGE_FLOAT64             Merges FLOAT64-initialized KLL sketches into a new sketch, and then gets the quantiles from the new sketch.
KLL_QUANTILES.MERGE_PARTIAL             Merges KLL sketches of the same underlying type into a new sketch.
KLL_QUANTILES.MERGE_POINT_INT64         Merges INT64-initialized KLL sketches into a new sketch, and then gets a specific quantile from the new sketch.
KLL_QUANTILES.MERGE_POINT_FLOAT64       Merges FLOAT64-initialized KLL sketches into a new sketch, and then gets a specific quantile from the new sketch.
LABELS                                  Gets the labels associated with a graph element.
LAG                                     Gets a value for a preceding row.
LAST_DAY                                Gets the last day in a specified time period that contains a DATE value.
LAST_DAY                                Gets the last day in a specified time period that contains a DATETIME value.
LAST_VALUE                              Gets a value for the last row in the current window frame.
LAX_BOOL                                Attempts to convert a JSON value to a SQL BOOL value.
LAX_FLOAT64                             Attempts to convert a JSON value to a SQL FLOAT64 value.
LAX_INT64                               Attempts to convert a JSON value to a SQL INT64 value.
LAX_STRING                              Attempts to convert a JSON value to a SQL STRING value.
LEAD                                    Gets a value for a subsequent row.
LEAST                                   Gets the least value among X1,...,XN.
LEFT                                    Gets the specified leftmost portion from a STRING or BYTES value.
LENGTH                                  Gets the length of a STRING or BYTES value.
LN                                      Computes the natural logarithm of X.
LOG                                     Computes the natural logarithm of X or the logarithm of X to base Y.
LOG10                                   Computes the natural logarithm of X to base 10.
LOGICAL_AND                             Gets the logical AND of all non-NULL expressions.
LOGICAL_OR                              Gets the logical OR of all non-NULL expressions.
LOWER                                   Formats alphabetic characters in a STRING value as lowercase. Formats ASCII characters in a BYTES value as lowercase.
LPAD                                    Prepends a STRING or BYTES value with a pattern.
LTRIM                                   Identical to the TRIM function, but only removes leading characters.
MAKE_INTERVAL                           Constructs an INTERVAL value.
MAX                                     Gets the maximum non-NULL value.
MAX_BY                                  Synonym for ANY_VALUE(x HAVING MAX y).
MD5                                     Computes the hash of a STRING or BYTES value, using the MD5 algorithm.
MIN                                     Gets the minimum non-NULL value.
MIN_BY                                  Synonym for ANY_VALUE(x HAVING MIN y).
MOD                                     Gets the remainder of the division of X by Y.
NET.HOST                                Gets the hostname from a URL.
NET.IP_FROM_STRING                      Converts an IPv4 or IPv6 address from a STRING value to a BYTES value in network byte order.
NET.IP_NET_MASK                         Gets a network mask.
NET.IP_TO_STRING                        Converts an IPv4 or IPv6 address from a BYTES value in network byte order to a STRING value.
NET.IP_TRUNC                            Converts a BYTES IPv4 or IPv6 address in network byte order to a BYTES subnet address.
NET.IPV4_FROM_INT64                     Converts an IPv4 address from an INT64 value to a BYTES value in network byte order.
NET.IPV4_TO_INT64                       Converts an IPv4 address from a BYTES value in network byte order to an INT64 value.
NET.PUBLIC_SUFFIX                       Gets the public suffix from a URL.
NET.REG_DOMAIN                          Gets the registered or registrable domain from a URL.
NET.SAFE_IP_FROM_STRING                 Similar to the NET.IP_FROM_STRING, but returns NULL instead of producing an error if the input is invalid.
NODES                                   Gets the nodes in a graph path. The resulting array retains the original order in the graph path.
NORMALIZE                               Case-sensitively normalizes the characters in a STRING value.
NORMALIZE_AND_CASEFOLD                  Case-insensitively normalizes the characters in a STRING value.
NTH_VALUE                               Gets a value for the Nth row of the current window frame.
NTILE                                   Gets the quantile bucket number (1-based) of each row within a window.
OBJ.FETCH_METADATA                      Fetches Cloud Storage metadata for a partially populated ObjectRef value.
OBJ.GET_ACCESS_URL                      Returns access URLs for a Cloud Storage object.
OBJ.GET_READ_URL                        Returns a read URL and status for a Cloud Storage object.
OBJ.MAKE_REF                            Creates an ObjectRef value that contains reference information for a Cloud Storage object.
OCTET_LENGTH                            Alias for BYTE_LENGTH.
PARSE_BIGNUMERIC                        Converts a STRING value to a BIGNUMERIC value.
PARSE_DATE                              Converts a STRING value to a DATE value.
PARSE_DATETIME                          Converts a STRING value to a DATETIME value.
PARSE_JSON                              Converts a JSON-formatted STRING value to a JSON value.
PARSE_NUMERIC                           Converts a STRING value to a NUMERIC value.
PARSE_TIME                              Converts a STRING value to a TIME value.
PARSE_TIMESTAMP                         Converts a STRING value to a TIMESTAMP value.
PATH_FIRST                              Gets the first node in a graph path.
PATH_LAST                               Gets the last node in a graph path.
PATH_LENGTH                             Gets the number of edges in a graph path.
PERCENT_RANK                            Gets the percentile rank (from 0 to 1) of each row within a window.
PERCENTILE_CONT                         Computes the specified percentile for a value, using linear interpolation.
PERCENTILE_CONT (Differential Privacy)  DIFFERENTIAL_PRIVACY-supported PERCENTILE_CONT. Computes a differentially-private percentile across privacy unit columns in a query with a DIFFERENTIAL_PRIVACY clause.
PERCENTILE_DISC                         Computes the specified percentile for a discrete value.
POW                                     Produces the value of X raised to the power of Y.
POWER                                   Synonym of POW.
RAND                                    Generates a pseudo-random value of type FLOAT64 in the range of [0, 1).
RANGE                                   Constructs a range of DATE, DATETIME, or TIMESTAMP values.
RANGE_BUCKET                            Scans through a sorted array and returns the 0-based position of a point's upper bound.
RANGE_CONTAINS                          Signature 1: Checks if one range is in another range. Signature 2: Checks if a value is in a range.
RANGE_END                               Gets the upper bound of a range.
RANGE_INTERSECT                         Gets a segment of two ranges that intersect.
RANGE_OVERLAPS                          Checks if two ranges overlap.
RANGE_SESSIONIZE                        Produces a table of sessionized ranges.
RANGE_START                             Gets the lower bound of a range.
RANK                                    Gets the rank (1-based) of each row within a window.
REGEXP_CONTAINS                         Checks if a value is a partial match for a regular expression.
REGEXP_EXTRACT                          Produces a substring that matches a regular expression.
REGEXP_EXTRACT_ALL                      Produces an array of all substrings that match a regular expression.
REGEXP_INSTR                            Finds the position of a regular expression match in a value, optionally starting the search at a given offset or occurrence.
REGEXP_REPLACE                          Produces a STRING value where all substrings that match a regular expression are replaced with a specified value.
REGEXP_SUBSTR                           Synonym for REGEXP_EXTRACT.
REPEAT                                  Produces a STRING or BYTES value that consists of an original value, repeated.
REPLACE                                 Replaces all occurrences of a pattern with another pattern in a STRING or BYTES value.
REVERSE                                 Reverses a STRING or BYTES value.
RIGHT                                   Gets the specified rightmost portion from a STRING or BYTES value.
ROUND                                   Rounds X to the nearest integer or rounds X to N decimal places after the decimal point.
ROW_NUMBER                              Gets the sequential row number (1-based) of each row within a window.
RPAD                                    Appends a STRING or BYTES value with a pattern.
RTRIM                                   Identical to the TRIM function, but only removes trailing characters.
S2_CELLIDFROMPOINT                      Gets the S2 cell ID covering a point GEOGRAPHY value.
S2_COVERINGCELLIDS                      Gets an array of S2 cell IDs that cover a GEOGRAPHY value.
SAFE_ADD                                Equivalent to the addition operator (X + Y), but returns NULL if overflow occurs.
SAFE_CAST                               Similar to the CAST function, but returns NULL when a runtime error is produced.
SAFE_CONVERT_BYTES_TO_STRING            Converts a BYTES value to a STRING value and replace any invalid UTF-8 characters with the Unicode replacement character, U+FFFD.
SAFE_DIVIDE                             Equivalent to the division operator (X / Y), but returns NULL if an error occurs.
SAFE_MULTIPLY                           Equivalent to the multiplication operator (X * Y), but returns NULL if overflow occurs.
SAFE_NEGATE                             Equivalent to the unary minus operator (-X), but returns NULL if overflow occurs.
SAFE_SUBTRACT                           Equivalent to the subtraction operator (X - Y), but returns NULL if overflow occurs.
SEARCH                                  Checks to see whether a table or other search data contains a set of search terms.
SEC                                     Computes the secant of X.
SECH                                    Computes the hyperbolic secant of X.
SESSION_USER                            Get the email address or principal identifier of the user that's running the query.
SHA1                                    Computes the hash of a STRING or BYTES value, using the SHA-1 algorithm.
SHA256                                  Computes the hash of a STRING or BYTES value, using the SHA-256 algorithm.
SHA512                                  Computes the hash of a STRING or BYTES value, using the SHA-512 algorithm.
SIGN                                    Produces -1 , 0, or +1 for negative, zero, and positive arguments respectively.
SIN                                     Computes the sine of X.
SINH                                    Computes the hyperbolic sine of X.
SOURCE_NODE_ID                          Gets a unique identifier of a graph edge's source node.
SOUNDEX                                 Gets the Soundex codes for words in a STRING value.
SPLIT                                   Splits a STRING or BYTES value, using a delimiter.
SQRT                                    Computes the square root of X.
ST_ANGLE                                Takes three point GEOGRAPHY values, which represent two intersecting lines, and returns the angle between these lines.
ST_AREA                                 Gets the area covered by the polygons in a GEOGRAPHY value.
ST_ASBINARY                             Converts a GEOGRAPHY value to a BYTES WKB geography value.
ST_ASGEOJSON                            Converts a GEOGRAPHY value to a STRING GeoJSON geography value.
ST_ASTEXT                               Converts a GEOGRAPHY value to a STRING WKT geography value.
ST_AZIMUTH                              Gets the azimuth of a line segment formed by two point GEOGRAPHY values.
ST_BOUNDARY                             Gets the union of component boundaries in a GEOGRAPHY value.
ST_BOUNDINGBOX                          Gets the bounding box for a GEOGRAPHY value.
ST_BUFFER                               Gets the buffer around a GEOGRAPHY value, using a specific number of segments.
ST_BUFFERWITHTOLERANCE                  Gets the buffer around a GEOGRAPHY value, using tolerance.
ST_CENTROID                             Gets the centroid of a GEOGRAPHY value.
ST_CENTROID_AGG                         Gets the centroid of a set of GEOGRAPHY values.
ST_CLOSESTPOINT                         Gets the point on a GEOGRAPHY value which is closest to any point in a second GEOGRAPHY value.
ST_CLUSTERDBSCAN                        Performs DBSCAN clustering on a group of GEOGRAPHY values and produces a 0-based cluster number for this row.
ST_CONTAINS                             Checks if one GEOGRAPHY value contains another GEOGRAPHY value.
ST_CONVEXHULL                           Returns the convex hull for a GEOGRAPHY value.
ST_COVEREDBY                            Checks if all points of a GEOGRAPHY value are on the boundary or interior of another GEOGRAPHY value.
ST_COVERS                               Checks if all points of a GEOGRAPHY value are on the boundary or interior of another GEOGRAPHY value.
ST_DIFFERENCE                           Gets the point set difference between two GEOGRAPHY values.
ST_DIMENSION                            Gets the dimension of the highest-dimensional element in a GEOGRAPHY value.
ST_DISJOINT                             Checks if two GEOGRAPHY values are disjoint (don't intersect).
ST_DISTANCE                             Gets the shortest distance in meters between two GEOGRAPHY values.
ST_DUMP                                 Returns an array of simple GEOGRAPHY components in a GEOGRAPHY value.
ST_DWITHIN                              Checks if any points in two GEOGRAPHY values are within a given distance.
ST_ENDPOINT                             Gets the last point of a linestring GEOGRAPHY value.
ST_EQUALS                               Checks if two GEOGRAPHY values represent the same GEOGRAPHY value.
ST_EXTENT                               Gets the bounding box for a group of GEOGRAPHY values.
ST_EXTERIORRING                         Returns a linestring GEOGRAPHY value that corresponds to the outermost ring of a polygon GEOGRAPHY value.
ST_GEOGFROM                             Converts a STRING or BYTES value into a GEOGRAPHY value.
ST_GEOGFROMGEOJSON                      Converts a STRING GeoJSON geometry value into a GEOGRAPHY value.
ST_GEOGFROMTEXT                         Converts a STRING WKT geometry value into a GEOGRAPHY value.
ST_GEOGFROMWKB                          Converts a BYTES or hexadecimal-text STRING WKT geometry value into a GEOGRAPHY value.
ST_GEOGPOINT                            Creates a point GEOGRAPHY value for a given longitude and latitude.
ST_GEOGPOINTFROMGEOHASH                 Gets a point GEOGRAPHY value that's in the middle of a bounding box defined in a STRING GeoHash value.
ST_GEOHASH                              Converts a point GEOGRAPHY value to a STRING GeoHash value.
ST_GEOMETRYTYPE                         Gets the Open Geospatial Consortium (OGC) geometry type for a GEOGRAPHY value.
ST_HAUSDORFFDISTANCE                    Gets the discrete Hausdorff distance between two geometries.
ST_HAUSDORFFDWITHIN                     Checks if the Hausdorff distance between two GEOGRAPHY values is within a given distance.
ST_INTERIORRINGS                        Gets the interior rings of a polygon GEOGRAPHY value.
ST_INTERSECTION                         Gets the point set intersection of two GEOGRAPHY values.
ST_INTERSECTS                           Checks if at least one point appears in two GEOGRAPHY values.
ST_INTERSECTSBOX                        Checks if a GEOGRAPHY value intersects a rectangle.
ST_ISCLOSED                             Checks if all components in a GEOGRAPHY value are closed.
ST_ISCOLLECTION                         Checks if the total number of points, linestrings, and polygons is greater than one in a GEOGRAPHY value.
ST_ISEMPTY                              Checks if a GEOGRAPHY value is empty.
ST_ISRING                               Checks if a GEOGRAPHY value is a closed, simple linestring.
ST_LENGTH                               Gets the total length of lines in a GEOGRAPHY value.
ST_LINEINTERPOLATEPOINT                 Gets a point at a specific fraction in a linestring GEOGRAPHY value.
ST_LINELOCATEPOINT                      Gets a section of a linestring GEOGRAPHY value between the start point and a point GEOGRAPHY value.
ST_LINESUBSTRING                        Gets a segment of a single linestring at a specific starting and ending fraction.
ST_MAKELINE                             Creates a linestring GEOGRAPHY value by concatenating the point and linestring vertices of GEOGRAPHY values.
ST_MAKEPOLYGON                          Constructs a polygon GEOGRAPHY value by combining a polygon shell with polygon holes.
ST_MAKEPOLYGONORIENTED                  Constructs a polygon GEOGRAPHY value, using an array of linestring GEOGRAPHY values. The vertex ordering of each linestring determines the orientation of each polygon ring.
ST_MAXDISTANCE                          Gets the longest distance between two non-empty GEOGRAPHY values.
ST_NPOINTS                              An alias of ST_NUMPOINTS.
ST_NUMGEOMETRIES                        Gets the number of geometries in a GEOGRAPHY value.
ST_NUMPOINTS                            Gets the number of vertices in the a GEOGRAPHY value.
ST_PERIMETER                            Gets the length of the boundary of the polygons in a GEOGRAPHY value.
ST_POINTN                               Gets the point at a specific index of a linestring GEOGRAPHY value.
ST_REGIONSTATS                          Computes statistics describing the pixels in a geospatial raster image that intersect a GEOGRAPHY value.
ST_SIMPLIFY                             Converts a GEOGRAPHY value into a simplified GEOGRAPHY value, using tolerance.
ST_SNAPTOGRID                           Produces a GEOGRAPHY value, where each vertex has been snapped to a longitude/latitude grid.
ST_STARTPOINT                           Gets the first point of a linestring GEOGRAPHY value.
ST_TOUCHES                              Checks if two GEOGRAPHY values intersect and their interiors have no elements in common.
ST_UNION                                Gets the point set union of multiple GEOGRAPHY values.
ST_UNION_AGG                            Aggregates over GEOGRAPHY values and gets their point set union.
ST_WITHIN                               Checks if one GEOGRAPHY value contains another GEOGRAPHY value.
ST_X                                    Gets the longitude from a point GEOGRAPHY value.
ST_Y                                    Gets the latitude from a point GEOGRAPHY value.
STARTS_WITH                             Checks if a STRING or BYTES value is a prefix of another value.
STDDEV                                  An alias of the STDDEV_SAMP function.
STDDEV_POP                              Computes the population (biased) standard deviation of the values.
STDDEV_SAMP                             Computes the sample (unbiased) standard deviation of the values.
STRING (JSON)                           Converts a JSON string to a SQL STRING value.
STRING (Timestamp)                      Converts a TIMESTAMP value to a STRING value.
STRING_AGG                              Concatenates non-NULL STRING or BYTES values.
STRPOS                                  Finds the position of the first occurrence of a subvalue inside another value.
SUBSTR                                  Gets a portion of a STRING or BYTES value.
SUBSTRING                               Alias for SUBSTR
SUM                                     Gets the sum of non-NULL values.
SUM (Differential Privacy)              DIFFERENTIAL_PRIVACY-supported SUM. Gets the differentially-private sum of non-NULL, non-NaN values in a query with a DIFFERENTIAL_PRIVACY clause.
TAN                                     Computes the tangent of X.
TANH                                    Computes the hyperbolic tangent of X.
TEXT_ANALYZE                            Extracts terms (tokens) from text and converts them into a tokenized document.
TF_IDF                                  Evaluates how relevant a term (token) is to a tokenized document in a set of tokenized documents.
TIME                                    Constructs a TIME value.
TIME_ADD                                Adds a specified time interval to a TIME value.
TIME_DIFF                               Gets the number of unit boundaries between two TIME values at a particular time granularity.
TIME_SUB                                Subtracts a specified time interval from a TIME value.
TIME_TRUNC                              Truncates a TIME value at a particular granularity.
TIMESTAMP                               Constructs a TIMESTAMP value.
TIMESTAMP_ADD                           Adds a specified time interval to a TIMESTAMP value.
TIMESTAMP_BUCKET                        Gets the lower bound of the timestamp bucket that contains a timestamp.
TIMESTAMP_DIFF                          Gets the number of unit boundaries between two TIMESTAMP values at a particular time granularity.
TIMESTAMP_MICROS                        Converts the number of microseconds since 1970-01-01 00:00:00 UTC to a TIMESTAMP.
TIMESTAMP_MILLIS                        Converts the number of milliseconds since 1970-01-01 00:00:00 UTC to a TIMESTAMP.
TIMESTAMP_SECONDS                       Converts the number of seconds since 1970-01-01 00:00:00 UTC to a TIMESTAMP.
TIMESTAMP_SUB                           Subtracts a specified time interval from a TIMESTAMP value.
TIMESTAMP_TRUNC                         Truncates a TIMESTAMP or DATETIME value at a particular granularity.
TO_BASE32                               Converts a BYTES value to a base32-encoded STRING value.
TO_BASE64                               Converts a BYTES value to a base64-encoded STRING value.
TO_CODE_POINTS                          Converts a STRING or BYTES value into an array of extended ASCII code points.
TO_HEX                                  Converts a BYTES value to a hexadecimal STRING value.
TO_JSON                                 Converts a SQL value to a JSON value.
TO_JSON_STRING                          Converts a SQL value to a JSON-formatted STRING value.
TRANSLATE                               Within a value, replaces each source character with the corresponding target character.
TRIM                                    Removes the specified leading and trailing Unicode code points or bytes from a STRING or BYTES value.
TRUNC                                   Rounds a number like ROUND(X) or ROUND(X, N), but always rounds towards zero and never overflows.
TYPEOF                                  Gets the name of the data type for an expression.
UNICODE                                 Gets the Unicode code point for the first character in a value.
UNIX_DATE                               Converts a DATE value to the number of days since 1970-01-01.
UNIX_MICROS                             Converts a TIMESTAMP value to the number of microseconds since 1970-01-01 00:00:00 UTC.
UNIX_MILLIS                             Converts a TIMESTAMP value to the number of milliseconds since 1970-01-01 00:00:00 UTC.
UNIX_SECONDS                            Converts a TIMESTAMP value to the number of seconds since 1970-01-01 00:00:00 UTC.
UPPER                                   Formats alphabetic characters in a STRING value as uppercase. Formats ASCII characters in a BYTES value as uppercase.
VAR_POP                                 Computes the population (biased) variance of the values.
VAR_SAMP                                Computes the sample (unbiased) variance of the values.
VARIANCE                                An alias of VAR_SAMP.
VECTOR_SEARCH                           Performs a vector search on embeddings to find semantically similar entities.
VECTOR_INDEX.STATISTICS                 Calculate how much an indexed table's data has drifted between when a vector index was trained and the present.
'''