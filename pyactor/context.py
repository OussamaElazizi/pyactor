from urlparse import urlparse
from actor import Actor,ActorRef
from proxy import Proxy
from tcp import TCPDispatcher
from util import *
import signal, sys
from time import sleep


class Host(object):
    _tell = ['shutdown']
    _ask = ['spawn','lookup','spawn_n','lookup2']

    def __init__(self,url):
        self.load_transport(url)

    def load_transport(self, url):
        aurl = urlparse(url)
        self.transport = aurl.scheme
        self.host_url = aurl
        if aurl.scheme == 'tcp':
            self.dispatcher = TCPDispatcher(aurl)
            launch_actor('tcp',self.dispatcher)



            #self.aref = 'atom://' + self.dispatcher.name + '/controller/Host/0'
            #self.name = self.dispatcher.name

    def spawn(self,id,klass,args=[]):
        url = '%s://%s/%s' % (self.transport,self.host_url.netloc,id)
        if actors.has_key(url):
            raise AlreadyExists()
        else:
            new_actor = Actor(url,klass,args)
            launch_actor(url,new_actor)
            return Proxy(new_actor)


    def spawn_n(self,n,id,klass,args=[]):
      #  url = 'local://name/'+id
        if actors.has_key(id):
            raise AlreadyExists()
        else:
            group  = [Actor(id,klass,args) for i in range(n)]
            for elem in group[1:]:
                elem.channel = group[0].channel
            for new_actor in group:
                launch_actor(id,new_actor)
            return Proxy(new_actor)

    def lookup(self,id):
        url =  '%s://%s/%s' % (self.transport,self.host_url.netloc,id)
        if actors.has_key(id):
            return Proxy(actors[url])
        else:
            raise NotFound()

    # problem with spawn_n and sample3.py.
    def shutdown(self):
        for actor in actors.values():
            Proxy(actor).stop()


    def lookup_url(self, url,klass):
        if self.is_local(aurl):
            if not actors.has_key(url):
                raise NotFound(url)
            else:
                return Proxy(actors[url])
        else:
            remote_actor = ActorRef(url,klass,self.dispatcher.channel)
            return Proxy(remote_actor)

    def is_local(self,url):
        aurl = urlparse(aref)
        return self.host_url.netloc == aurl.netloc




def launch_actor(id,actor):
    actor.run()
    actors[id] = actor
    threads[actor.thread] = id


def init_host(url='local://local/host'):
    host = Actor(url,Host,[url])
    launch_actor(url,host)
    global _host
    _host = Proxy(host)
    return _host


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    _host.shutdown()
    sys.exit(0)


def serve_forever():
    signal.signal(signal.SIGINT, signal_handler)
    print 'Press Ctrl+C to kill the execution'
    while True:
        sleep(1)
