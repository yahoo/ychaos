#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

if [ "$CODECOV_TOKEN" != "" ]; then
    $BASE_PYTHON -m pip install codecov

    if [ -z $SD_PULL_REQUEST ];
    then
        codecov -c ${SD_BUILD_SHA} --build ${SD_BUILD_ID} --tries 2
    else
        codecov --pr ${SD_PULL_REQUEST} -c ${SD_BUILD_SHA} --build ${SD_BUILD_ID} --tries 2
    fi
fi
