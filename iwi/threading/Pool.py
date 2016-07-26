import Queue
import sys
import threading

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = ['Pool']

class Pool (object):
    """
    Simplistic thread pool.
    """
    class WorkerExit (object):
        """
        Sentinel class used to shut down threads.
        """
        def __call__ (self):
            """
            Does nothing.
            """
            return None

    class Worker (threading.Thread):
        """
        Pool worker thread.
        """
        def __init__ (self, pool):
            """
            Initializes an instance from a parent pool.
            """
            super(Pool.Worker, self).__init__()
            self.pool = pool

        def run (self):
            """
            Spins on the job queue reading jobs and writing results.
            """
            obj = None

            while obj is not self.pool.sentinel:
                obj, args, kwargs = self.pool.job_queue.get()

                try:
                    res = obj(*args, **kwargs)

                    if res is not None:
                        self.pool.res_queue.put(res)
                except Exception as e:
                    logger.error('%s', e)
                finally:
                    self.pool.job_queue.task_done()

    sentinel = WorkerExit()

    def __init__ (self, num_threads=32, use_daemons=True):
        """
        Initializes an instance with a certain number of threads.
        """
        self.num_threads = num_threads
        self.job_queue   = Queue.Queue()
        self.res_queue   = Queue.Queue()
        self.threads     = []
        self.closed      = False

        for _ in xrange(self.num_threads):
            self.threads.append(Pool.Worker(self))

        for thread in self.threads:
            thread.daemon = use_daemons
            thread.start()

    def __enter__ (self):
        return self

    def __exit__ (self, *ignored):
        self.close()

    def close (self):
        """
        Properly destructs the pool by killing the threads.

        After executing this method the pool is no longer operational.
        """
        if self.closed:
            return

        # Guarantee that no unfinished jobs will be interleaved with the
        # sentinel values, a worker thread might add jobs while its running and
        # after we added the sentinels.
        self.join()

        for _ in xrange(self.num_threads):
            self.push(self.sentinel)

        for thread in self.threads:
            thread.join()

        self.closed = True

    def get_results (self):
        """
        Attemps to retrieve all results, calling this before calling join()
        might result in very weird behavior.
        """
        results = []

        while not self.res_queue.empty():
            results.append(self.res_queue.get())
            self.res_queue.task_done()

        return results

    def push (self, obj, *args, **kwargs):
        """
        Pushes a job onto the queue.

        If this pool is closed then a RuntimeError is raised.
        """
        if self.closed:
            raise RuntimeError ('Can\'t add jobs to a closed pool.')

        self.job_queue.put((obj, args, kwargs))

    def join (self):
        """
        Waits for every enqueued job to finish.
        """
        self.job_queue.join()
