#!/usr/bin/env bash

rm -f ./container/generic_loader/ubdcc_dcn
rm -f ./container/generic_loader/ubdcc_mgmt
rm -f ./container/generic_loader/ubdcc_restapi
rm -f ./container/generic_loader/ubdcc_shared_modules

rm -f ./packages/ubdcc-dcn/ubdcc_shared_modules
rm -f ./packages/ubdcc-dcn/ubdcc_dcn/ubdcc_shared_modules

rm -f ./packages/ubdcc-mgmt/ubdcc_shared_modules
rm -f ./packages/ubdcc-mgmt/ubdcc_mgmt/ubdcc_shared_modules

rm -f ./packages/ubdcc-restapi/ubdcc_shared_modules
rm -f ./packages/ubdcc-restapi/ubdcc_restapi/ubdcc_shared_modules