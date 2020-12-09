
import time
import curses
import requests
import json
import sys
import urllib.parse
import logging
import pkgutil
import yaml
import atexit
import pathlib

# Initialize curses

def setup_curses():
    """setup curses library"""
    # Turn off echoing of keys, and enter cbreak mode,
    # where no buffering is performed on keyboard input
    curses.noecho()
    curses.cbreak()
    # hide cursor
    curses.curs_set(0)
    # In keypad mode, escape sequences for special keys
    # (like the cursor keys) will be interpreted and
    # a special value like curses.KEY_LEFT will be returned
    stdscr.keypad(1)
        
def reset_curses():
    """reset curses library"""
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


atexit.register(reset_curses)
stdscr = curses.initscr()

class Dashboard:
    def __init__(self, stdscr, refresh_interval):
        """init dashboard"""
        self.refresh_interval = refresh_interval
        self.stdscr = stdscr
        self.lineno = 0
        self.nb_col = 2
        
        self.sw = 0
        self.sh = 0
        self.bw = 0
        self.bh = 10

        self.scroll_begin = 0
        self.rows_col1 = []
        self.rows_col2 = []

    def scroll_up(self):
        if self.scroll_begin == 0:
            return
        self.scroll_begin -= 1 
        
    def scroll_down(self): 
        height, width = self.stdscr.getmaxyx()
  
        if self.scroll_begin == len(self.rows_col1):
            return

        if height > 0:
            if len(self.rows_col1[self.scroll_begin:])  < height-5:
                return
            
        self.scroll_begin += 1

    def get_screen_size(self):
        """get screen size"""
        self.sh, self.sw = self.stdscr.getmaxyx()
        self.bw = int(self.sw)//self.nb_col
                    
    def draw_line(self, text, pos, attr=0):
        """add line to the dashboard"""
        try:
            self.stdscr.addstr(self.lineno, pos, text, attr)
        except curses.error:
            pass
        self.lineno += 1
   
    def draw_title(self, stream):
        """draw title"""
        # print title and header
        stream_name = stream["stream"] if stream["stream"] is not None else "all"
        title = [ "dnstap dashboard [stream: %s]" % stream_name, 
                  "refreshed every %s second(s)" % self.refresh_interval ]
        title = " / ".join(title)     
        
        text = title + " " * (self.bw*self.nb_col-len(title)-2)
        self.draw_line(text=text, pos=1, attr=curses.A_REVERSE)

    def draw_header(self, cnts):
        """draw header"""
        q = [ "queries: %s total" % cnts["query"] ]
        q.append( "%s qps" % cnts["qps"] )
        q.append( "%s udp, %s tcp" % (cnts["query/udp"], cnts["query/tcp"]) )
        q.append( "%s ip4, %s ip6" % (cnts["query/inet"], cnts["query/inet6"]) )
        q.append( "%s clients" % cnts["clients"] )
        self.draw_line(text=", ".join(q), pos=1)
        
        q = [ "responses: %s total" % cnts["response"] ]
        
        q.append( "%s udp, %s tcp" % (cnts["response/udp"], cnts["response/tcp"]) )
        q.append( "%s ip4, %s ip6" % (cnts["response/inet"], cnts["response/inet6"]) )
        self.draw_line(text=", ".join(q), pos=1)
        
        q = [ "domains: %s total" % cnts["domains"]  ]
        q.append("%s noerror" % cnts["response/noerror"] )
        q.append("%s nxdomain"  % cnts["response/nxdomain"] )
        
        self.draw_line(text=", ".join(q), pos=1)
        self.draw_line(text="\n", pos=0)        

    def draw_footer(self):
        """draw footer"""
        footer = "[Q]uit | [N]ext stream | Up/down to scroll"
        pad_footer = " " * ((self.sw-len(footer))-2)
        self.stdscr.addstr(self.sh-1, 1, footer+pad_footer, curses.A_REVERSE)
        
    def draw_box(self, rows, pos):
        """draw a box"""
        for row in rows[self.scroll_begin:]:
            if isinstance(row, tuple):
                attr, text = row
                title_box = text.upper()
                pad_box = " " * (self.bw-len(title_box)-len("HITS")-3)
                self.draw_line(text=title_box+pad_box+"TOTAL", pos=pos, attr=curses.A_REVERSE)
            else:
                self.draw_line(text=row, pos=pos, attr=0)

    def onrefresh(self, data):
        """refresh the dashboard"""
        cnts = data["counters"]["counters"]
        
        # erase the screen before to refresh
        self.stdscr.erase()
        
        # recalculate box size according to the screen
        self.get_screen_size()

        # draw title
        self.draw_title(stream=data["counters"])
        
        # draw header
        self.draw_header(cnts=cnts)
        
        # prepare rows for top boxes
        self.rows_col1.clear()
        self.rows_col2.clear()

        for i in range(len(data["top"])):
            if (i % self.nb_col) == 0:
                dest = self.rows_col1
            else:
                dest = self.rows_col2
            
            top_descr =  "%s" % data["top"][i]["description"]
            dest.append( ((curses.A_UNDERLINE | curses.A_BOLD ),top_descr) )
            
            rows = data["top"][i]["rows"]
            rows.extend([("", "")]* (self.bh-len(rows)) )

            for j in range(len(rows)):
                entry_n, entry_g = rows[j]
                
                if len(entry_n) > (self.bw-10):
                    entry_n = "%s..." % entry_n[:self.bw-14]
                entry_g = "%s" % entry_g
                entry_i = "%s." % (j+1)
                pad_entry = " " * (self.bw-len(entry_i)-len(entry_n)-len(entry_g)-4)

                entry = "%s %s %s" %(entry_i, entry_n + pad_entry, entry_g)
                dest.append( entry )
            dest.append( "" )

        # draw the first column
        self.draw_box(rows=self.rows_col1, pos=1)
        
        # draw the second column
        self.lineno -= len(self.rows_col1[self.scroll_begin:])
        self.draw_box(rows=self.rows_col2, pos=self.bw+1)

        # add footer
        self.draw_footer()
        
        # refresh the screen and reset the line number
        self.stdscr.refresh()
        self.lineno = 0

    def keyboard_listener(self, scr, timeout, datafetcher):
        """listener for key press"""
        try:
            scr.timeout(timeout*1000)
            c = scr.getch()
            if c == ord('q'):
                raise KeyboardInterrupt()
            elif c == curses.KEY_UP:
                self.scroll_up()
            elif c == curses.KEY_DOWN:
                self.scroll_down()
            elif c == curses.KEY_LEFT:
                datafetcher.previous_stream()
            elif c == curses.KEY_RIGHT:
                datafetcher.next_stream()
        except curses.error as e:
            pass
               
class DataFetcher:
    def __init__(self, api_key, api_host, api_port, cfg, timeout=2):
        """data fetcher"""
        self.conf = cfg
        self.api_host = api_host
        self.api_port = api_port
        self.api_key = api_key
        self.timeout = timeout
        self.cur_stream = None
        self.cur_index = 0
        self.streams = []
        
    def next_stream(self):
        """next stream"""
        self.cur_index +=1
        if self.cur_index == len(self.streams): 
            self.cur_index = len(self.streams)-1
            return

        self.cur_stream = self.streams[self.cur_index]
 
    def previous_stream(self):
        """select previous stream"""
        self.cur_index -= 1
        if self.cur_index == -1: 
            self.cur_index = 0
            return
            
        self.cur_stream = self.streams[self.cur_index]

    def make_http(self, endpoint):
        """make http request"""
        api_url = "http://%s:%s" % (self.api_host, self.api_port)
        api_url += endpoint
        headers={'X-API-Key': self.api_key}
        r = requests.get(url=api_url, headers=headers, 
                         timeout=self.timeout)
        if r.status_code != 200:
            raise Exception("unexpected status code %s from dnstap receiver" % r.status_code )
        else:
            return json.loads(r.text)
            
    def fetching(self):
        """fetching dnstap receiver"""
        data = {}
        
        # fetching streams list
        response = self.make_http(endpoint="/streams")
        self.streams = response["streams"]
        self.streams.insert(0, None)
        
        # fetching top metrics
        top = self.conf["top-items"]
        endpoint = "/tables?n=%s" % top
        if self.cur_stream is not None: endpoint += "&stream=%s" % self.cur_stream
        response = self.make_http(endpoint=endpoint)
        
        top_data = []
        for item in response["tables"]:
            if item == "streams": continue
            for topitem in self.conf["categories"]:
                 if topitem == item:
                    for flag in self.conf["categories"][topitem]:
                        top_item_data = {"description": flag["description"], 
                                         "rows": response["tables"][item].get(flag["tag"], []) }
                        top_data.append( top_item_data )
                
        data["top"] = top_data
        
        # fetching counters
        endpoint = "/counters?"
        endpoint += "more=query/udp,query/tcp,response/udp,response/tcp"
        endpoint += ",query/inet,query/inet6,response/inet,response/inet6"
        if self.cur_stream is not None: endpoint += "&stream=%s" % self.cur_stream
        response = self.make_http(endpoint=endpoint)
        data["counters"] = response

        return data

def load_yaml(f):
    """load yaml file"""
    try:
        cfg =  yaml.safe_load(f) 
    except FileNotFoundError:
        print("default config file not found")
        sys.exit(1)
    except yaml.parser.ParserError:
        print("invalid default yaml config file")
        sys.exit(1)
    return cfg    
    
def merge_cfg(u, o):
    """merge config"""
    for k,v in u.items():
        if k in o:
            if isinstance(v, dict):
                merge_cfg(u=v,o=o[k])
            else:
                o[k] = v
   
def setup_config():
    # set default config
    f = pkgutil.get_data(__package__, 'dashboard.conf')
    cfg = load_yaml(f)
    
    # loading config file from etc ?
    ext_cfg_path = "/etc/dnstap_dashboard/dashboard.conf"
    f = pathlib.Path(ext_cfg_path)
    if f.exists():
        cfg_ext = load_yaml(open(ext_cfg_path, 'r'))
        merge_cfg(u=cfg_ext,o=cfg)
        
    return cfg
    
def start_dashboard():
    conf = setup_config()
    
    error_caught = False
    last_error = None

    # setup curses
    setup_curses()
    
    try:
        stdscr.addstr(0, 0, "Loading dnstap dashboard...")
        datafetcher = DataFetcher(api_key=conf["dnstap-receiver"]["api-key"], 
                                  api_host=conf["dnstap-receiver"]["api-ip"], 
                                  api_port=conf["dnstap-receiver"]["api-port"],
                                  cfg=conf)
        dashboard = Dashboard(stdscr=stdscr,
                              refresh_interval=conf["refresh-interval"] )
        t = 0
        while True:
            # listen for keyboard press
            dashboard.keyboard_listener(stdscr, t, datafetcher)
            # fetching data from dnstap receiver
            data = datafetcher.fetching()
            # and refresh the dashboard
            dashboard.onrefresh(data=data)
            # sleep time in second for next run
            t = conf["refresh-interval"] 
    except (KeyboardInterrupt):
        pass
    except Exception as e:
        error_caught = True
        last_error = e
    finally:
        reset_curses()
        
    if error_caught:
        logging.error("%s" % last_error)