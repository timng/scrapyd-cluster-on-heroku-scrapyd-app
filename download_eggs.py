import sys
import io
import ftplib 
import os
 
def list_all_ftp_files(ftp, dir):
    dirs = []
    non_dirs = []
  
    '''Capture the print output of ftp.dir'''
    stream = io.StringIO()
    sys.stdout = stream
    ftp.dir(dir)
    streamed_result = stream.getvalue()   
  
    reduced = [x for x in streamed_result.split(' ') if x != '']
  
    '''Clean up list'''
    reduced = [x.split('\n')[0] for x in reduced]
  
    '''Get the names of the folders by which ones are labeled <DIR>'''
    indexes = [ix + 1 for ix,x in enumerate(reduced) if x == '<DIR>']
  
    folders = [reduced[ix] for ix in indexes]
      
    if dir == '/':
        non_folders = [x for x in ftp.nlst() if x not in folders]
    else:
        non_folders = [x for x in ftp.nlst(dir) if x not in folders]
        non_folders = [dir + '/' + x for x in non_folders]
        folders = [dir + '/' + x for x in folders]
          
    '''If currently scanning the root directory, just add the initial set of
       of folders in that directory to our grand list'''
    if dirs == []:
        dirs.extend(folders)
        '''Similarly, do the same for files that are not folders'''
    if non_dirs == []:
        non_dirs.extend(non_folders)
  
    '''If there are still sub-folders within a directory, keep searching deeper
       potential other sub-folders'''
    if len(folders) > 0:
        for sub_folder in sorted(folders):
            result = list_all_ftp_files(ftp, sub_folder)
            dirs.extend(result[0])
            non_dirs.extend(result[1])
  
    '''Return the list of all directories on the FTP Server, along
       with the list of all non-folder files'''
    return dirs , non_dirs
 
 
 
'''Connect to FTP site'''
ftp = ftplib.FTP('ftp.nasdaqtrader.com')
  
'''Login'''
ftp.login()
  
'''Get all folders and files on FTP Server'''
folders , files = list_all_ftp_files(ftp , '/')
 
 
'''Get IO streams for each file'''
file_mapper = {}
for file in files:
      
    r = io.BytesIO()
    ftp.retrbinary('RETR ' + file , r.write)
      
    file_mapper[file] = r
      
    r.close()
 
 
'''Write all files on FTP Server to disk'''
for key,val in file_mapper.items():
     
    '''Create directory structure if it doesn't exist'''
    if not os.path.exists(os.path.dirname(key)):
        os.makedirs(os.path.dirname(key))
     
    '''Check if file is a text file'''
    if len(key.split('.txt')) > 1:
        f = open(key , 'w+')
        f.write(val.decode())
        f.close()
    else:
        f = open(key , 'wb+')
        f.write(val)
        f.close()
