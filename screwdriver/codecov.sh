if [ "$CODECOV_TOKEN" != "" ]; then
    $BASE_PYTHON -m pip install codecov

    if [ -z $SD_PULL_REQUEST ];
    then
        codecov -c ${SD_BUILD_SHA} --build ${SD_BUILD_ID} --tries 2
    else
        codecov --pr ${SD_PULL_REQUEST} -c ${SD_BUILD_SHA} --build ${SD_BUILD_ID} --tries 2
    fi
fi
