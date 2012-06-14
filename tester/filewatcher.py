import os
from java.nio.file import FileSystems, StandardWatchEventKinds

def watch_file_for_changes(filename):
    watcher = FileSystems.getDefault().newWatchService()
    path = FileSystems.getDefault().getPath(os.path.dirname(filename))
    path.register(watcher, StandardWatchEventKinds.ENTRY_MODIFY)

    print 'Watching...'
    while 1:
        key = watcher.take()

        for event in key.pollEvents():
            if event.kind() == StandardWatchEventKinds.ENTRY_MODIFY:
                if str(event.context()) == os.path.basename(filename):
                    return True

        key.reset()

def main():
    print 'Watch 1'
    print watch_file_for_changes('/var/tmp/hello')

    print 'Watch 2'
    print watch_file_for_changes('/var/tmp/hello')

if __name__ == '__main__':
    main()
