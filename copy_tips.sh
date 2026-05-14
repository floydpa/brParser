#!/bin/ksh
# Once Telegram messages have been extracted into parser_out and parsed to produce tips in parser_output
# we can separate out the messages containing tips from all the other chatty messages.

MSGIDS=`ls parser_output | sed -e 's/_[0-9][0-9]*.json//' -e s'/^.*_//' | sort -u`
TARGET_DIR=tip_messages

for id in $MSGIDS; do
    cp parser_input/*_${id}.txt parser_input/*_${id}.json ${TARGET_DIR}/.
done

