#!/usr/bin/env bash

cd container/generic_loader/
ln -s ../../packages/ubdcc-dcn/ubdcc_dcn .
ln -s ../../packages/ubdcc-mgmt/ubdcc_mgmt .
ln -s ../../packages/ubdcc-restapi/ubdcc_restapi .
ln -s ../../packages/ubdcc-shared-modules/ubdcc_shared_modules .

cd ../../packages/ubdcc-dcn/
ln -s ../ubdcc-shared-modules/ubdcc_shared_modules .
cd ubdcc_dcn
ln -s ../ubdcc_shared_modules .

cd ../../ubdcc-mgmt/
ln -s ../ubdcc-shared-modules/ubdcc_shared_modules .
cd ubdcc_mgmt
ln -s ../ubdcc_shared_modules .

cd ../../ubdcc-restapi/
ln -s ../ubdcc-shared-modules/ubdcc_shared_modules .
cd ubdcc_restapi
ln -s ../ubdcc_shared_modules .


