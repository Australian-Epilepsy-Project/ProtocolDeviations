#!/usr/bin/env python3

import argparse
import pathlib
import sys
import pydicom

TO_NULL = [
    "ReferringPhysicianName",
    "ReferencedImageSequence",
    "PerformedProcedureStepDescription"
]

TO_ANONYMISE = [
    "InstitutionName",
    "InstitutionAddress",
    "StationName",
    "StudyDescription",
    "InstitutionalDepartmentName",
]

UIDS_TO_MODIFY = {
    "MediaStorageSOPInstanceUID": 8,
    "SOPInstanceUID": 8,
    "PatientID": 10,
    "StudyInstanceUID": 8,
    "SeriesInstanceUID": 8,
    "FrameOfReferenceUID": 8,
}

CSA = [
    (0x0029, 0x0010),
    (0x0029, 0x0011),
    (0x0029, 0x0012),
    (0x0029, 0x1008),
    (0x0029, 0x1009),
    (0x0029, 0x1010),
    (0x0029, 0x1018),
    (0x0029, 0x1019),
    (0x0029, 0x1020),
    (0x0029, 0x1110),
    (0x0029, 0x1120),
    (0x0029, 0x1220),
    (0x7FE1, 0x0010),
    (0x7FE1, 0x1010), # Large DTI Tensor data
]


def convert(indir, outdir):

    for path_dicom in (x for x in indir.rglob("*") if x.is_file() and pydicom.misc.is_dicom(x)):

        dicom = pydicom.dcmread(path_dicom)

        for to_null in TO_NULL:
            setattr(dicom, to_null, None)
        for to_anonymise in TO_ANONYMISE:
            try:
                setattr(dicom, to_anonymise, f"Anonymous{to_anonymise}")
            except AttributeError:
                pass
        for key, remove_idx in UIDS_TO_MODIFY.items():
            try:
                existing = getattr(dicom, key)
                splitbydot = existing.split('.')
                modified = '.'.join(splitbydot[0:remove_idx] + splitbydot[remove_idx+1:])
                setattr(dicom, key, pydicom.uid.UID(modified))
            except AttributeError:
                pass

        existing = dicom.file_meta.MediaStorageSOPInstanceUID
        splitbydot = existing.split('.')
        modified = '.'.join(splitbydot[0:8] + splitbydot[9:])
        dicom.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.UID(modified)

        # Erase CSA completely
        for csa in CSA:
            try:
                dicom[csa]
                del dicom[csa]
            except KeyError:
                continue

        # Erase pixel data
        delete_pixel_data = True

        # Special cases:
        # For session 004,
        #   do not erase additional scanner-derivative from MP2RAGE
        #if dicom.SeriesNumber == 12:
        #    delete_pixel_data = False
        # For session 010,
        #   do not erase the pixel data for DWI magnitude & phase
        #if dicom.SeriesNumber in (24, 25):
        #    delete_pixel_data = False
        # For sessions 011 and 012,
        #   preserve all spin-echo EPIs
        #if dicom.SeriesNumber in (16, 17, 19, 20, 22,23):
        #    delete_pixel_data = False
        # For session 013,
        #   preserve the unknown acquisition (pd_tse_tra)
        #if dicom.SeriesNumber == 16:
        #    delete_pixel_data = False

        if delete_pixel_data:
            try:
                del dicom.PixelData
            except AttributeError:
                pass

        # Change name of first directory to remove DaRIS IDs
        relpath = path_dicom.relative_to(indir)
        firstparent = str(relpath.parents[-2])
        daris_id = firstparent.split(' ')[0]
        seriesdescription = ' '.join(firstparent.split(' ')[1:])
        newdirname = f"{daris_id.split('.')[-1].zfill(2)}_{seriesdescription}"
        outpath = outdir / newdirname / path_dicom.relative_to(indir / firstparent)
        outpath.parents[0].mkdir(parents=True, exist_ok=True)
        dicom.save_as(outpath)


def main():

    parser = argparse.ArgumentParser("Anonymise & reduce ProtocolQC tutorial data")
    parser.add_argument("input", help="Input directory")
    parser.add_argument("output", help="Output directory")

    args = parser.parse_args()
    indir = pathlib.Path(args.input)
    outdir = pathlib.Path(args.output)

    if not indir.is_dir():
        sys.stderr.write("Error: Input directory does not exist\n")
        sys.exit(1)
    if outdir.exists():
        sys.stderr.write("Error: Output directory already exists\n")
        sys.exit(1)

    convert(indir, outdir)



if __name__ == "__main__":
    main()
