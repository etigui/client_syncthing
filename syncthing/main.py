
# External import
import argparse

# Internal import
import syncthing
import info


def main():

    # Parse user arguments
    parser = argparse.ArgumentParser("Syncthing client")
    parser.add_argument("-d", "--directory", dest="sync_directory",\
                        type=str, help="Main sync directory", required=True)
    parser.add_argument("-c", "--cert",dest="cert", type=str,\
                        help="Certificate file", required=True)
    parser.add_argument("-k", "--key", dest="key", type=str,\
                        help="Private key file", required=True)
    parser.add_argument("-i", "--ip", dest="ip", type=str,\
                        help="Server IP", required=True)
    parser.add_argument("-p", "--port", dest="port", type=int,\
                        help="Server port", required=True)
    parser.add_argument("-v", "--verbose", dest="verbose",\
                        help="Increase output verbosity", action="store_true", required=False)
    args = parser.parse_args()

    # Init client info
    user_info = info.Info(args.sync_directory, args.cert, args.key, args.ip, args.port, args.verbose)
    user_info.gen_device_id()

    # Init Syncthing
    process = syncthing.Syncthing(user_info)
    process.start()
    process.join()


if __name__ == "__main__":
    main()
