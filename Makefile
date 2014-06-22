prefix = $(DESTDIR)/usr
target_dir = $(prefix)/share/satori-uploader
bin_dir = $(prefix)/bin

all :
	@echo "Nothing to do"

install ::
	@mkdir -p $(target_dir) $(bin_dir)
	@cp -rv src/* $(target_dir)
	@ln -svf $(target_dir)/satori.sh $(bin_dir)/satori

uninstall ::
	@rm -rvf $(target_dir) $(bin_dir)/satori

clean ::
	@git clean

.PHONY : install uninstall clean
