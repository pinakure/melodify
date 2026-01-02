#!/bin/bash

for FILE in favicon-adaptative-*
do
    VALOR=$(echo "$FILE" | sed -E 's/^favicon-adaptative-(.*)$/\1/')
    cp favicon-adaptative-$VALOR favicon-square-$VALOR
    cp favicon-adaptative-$VALOR favicon-round-$VALOR
done
