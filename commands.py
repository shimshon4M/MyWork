"""
----- EBNF of NLP_LaTeX_templete ----- 
<wholepaper>    ::= <paperheader> <body>
<paperheader>   ::= <documentclass> | <documentstyle> | <usepackage> |
                    <setcounter> | <let> | <newcommand> | <setulminsep> |
                    <title> | <author> | <abstract> | <keywords> | <dateinfo> |
                    <affilabel> | <headtitle> | <headauthor>
<documentclass> ::= "\documentclass" "[" <string> "]" "{" <string> "}"
<documentstyle> ::= "\documentstyle" "[" <string> "]" "{" <string> "}"
<usepackage>    ::= "\usepackage" ["[" <string> "]"]* ["{" <string> "}"]*
<setcounter>    ::= "\setcounter" ["{" <string> "}"]*
<let>           ::= "\let" "\" <sttring>
<newcommand>    ::= "\newcommand" "{" "\" <string> "}" "{}"
<setulminsep>   ::= "\setulminsep" ["{" <string> "}"]*
<title>         ::= <jtitle> | <etitle>
<author>        ::= <jauthor> | <eauthor>
<abstract>      ::= <jabstract> | <eabstract>
<keywords>      ::= <jkeywords> | <ekeywords>
<jtitle>        ::= "\jtitle" "{" <statement> "}"
<etitle>        ::= "\etitle" "{" <statement> "}"
<jauthor>       ::= "\jauthor" "{" <authorinfo> ["\and" <authorinfo>]* "}"
<eauthor>       ::= "\jauthor" "{" <authorinfo> ["\and" <authorinfo>]* "}"
<authorinfo>    ::= <string> ["\affiref" "{" <string> "}"]*
<jabstract>     ::= "\jabstract" "{" <statement> "}"
<eabstract>     ::= "\eabstract" "{" <statement> "}"
<jkeywords>     ::= "\jkeywords" "{" <statement> "}"
<ekeywords>     ::= "\ekeywords" "{" <statement> "}"
<affilabel>     ::= "\affilabel" ["{" <statement> "}"]*
<headtitle>     ::= "\headtitle" "{" <statement> "}"
<headauthor>    ::= "\headauthor" "{" <statement> "}"
<body>          ::= "\begin" "{document}" [section]* <biodata> "\end" "{document}"
<dateinfo>      ::= <volume> | <number> | <month> | <year> | <received> |
                    <revised> | <accepted> | <uketsuke> | <saiuketsuke> |
                    <sairoku>
<volume>        ::= "\Volume" "{" <string> "}"
<number>        ::= "\Number" "{" <string> "}"
<month>         ::= "\Month" "{" <string> "}"
<year>          ::= "\Year" "{" <string> "}"
<received>      ::= "\received" ["{" <string> "}"]*
<revised>       ::= "\revised" ["{" <string> "}"]*
<accepted>      ::= "\accepted" ["{" <string> "}"]*
<uketsuke>      ::= "\受付" ["{" <string> "}"]*
<saiuketsuke>   ::= "\再受付" ["{" <string> "}"]*
<sairoku>       ::= "\再録" ["{" <string> "}"]*
<section>       ::= "\section" "{" <statement> "}" ["\label" "{" <statement> "}"] <statement>

<body>          ::= "\begin" "{document}" ["\maketitle"] [<section>]* [<acknowledgment>] <bioinfo>
                    "\end" "{document}"
<section>       ::= "\section" ["*"] "{" <statement> "}" ["\label" "{" <statement> "}"] <statement> [<subsection>]*
<subsection>    ::= "\subsection" ["*"] "{" <statement> "}" ["\label" "{" <statement> "}"] <statement> [<subsubsection>]*
<subsubsection> ::= "\subsubsection" ["*"] "{" <statement> "}" ["\label" "{" <statement> "}"] <statement>
                    
<acknowledgment>::= "\acknowledgment" <statement>
<biodata>       ::= <bibliographystyle> <bibliography> <biography> "\biodata"
<statement>     ::= [statement]* | <string> | 
                    <figure> | <table> | <cite> | <ref> | <replace> |
<string>        ::= [string]* | character | <decostring>
<decostring>    ::= "\textbf" "{" <string> "}" |
                    "\boldsymbol" "{" <string> "}" |
                    "\rm" "{" <string> "}" |
                    "{" "\bf" <string> "}"
<mathstring>    ::= "$"
<figure>        ::= "\begin" "{figure}" "\end" "{figure}"
<table>         ::= "\begin" "{table}" "\end" "{table}"
<gather>        ::= "\begin" "{gather}" "\end" "{gather}"
<cite>          ::= ("\cite"|"\citeyear") "{" <statement> "}"
<ref>           ::= "\ref" "{" <statement> "}" |

"""


$\mathrm{CO_2}$
$p$ #英数字
$関数_{変数}$
$関数_{変数}(？)$
\frac{分子}{分母}
\footnote{下部注釈}
\cite{引用}
\citeyear{引用}
\ref{参照セクション/表図ラベル}
{\allowdisplaybreaks}
\begin{equation}式\end{equation}
{\sf$<$文字列$>$}


エスケープシーケンス
\a
\b
\f
\r
\n
\t
\v
\N
\u
\U
\o
\x
\0
