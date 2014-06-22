prefix = $(DESTDIR)/usr/local
target_dir = $(prefix)/satori-uploader
bin_dir = $(prefix)/bin

all :
	@echo "Nothing to do"

install ::
	@mkdir -p $(prefix) $(bin_dir)
	@cp -rv src $(target_dir)
	@ln -svf $(target_dir)/satori.sh $(bin_dir)/satori

uninstall ::
	@rm -rvf $(target_dir) $(bin_dir)/satori

.PHONY : install uninstall
