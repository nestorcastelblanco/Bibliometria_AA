var hoverZoomPlugins = hoverZoomPlugins || [];
hoverZoomPlugins.push({
    name:'wixstatic_a',
    version:'0.2',
    prepareImgLinks:function (callback) {
        var res = [];

        // images
        //   samples: https://www.maya-altitude.com/basic-01
        // thumbnail: https://static.wixstatic.com/media/8d1934_58b641a6575843a7bdacc28b3d64e27d~mv2.jpg/v1/fill/w_103,h_69,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/8d1934_58b641a6575843a7bdacc28b3d64e27d~mv2.jpg
        //  fullsize: https://static.wixstatic.com/media/8d1934_58b641a6575843a7bdacc28b3d64e27d~mv2.jpg
        hoverZoom.urlReplace(res,
            'img[src*="static.wixstatic.com"]',
            /(^.*?~mv2\..*?)\/.*/,
            '$1'
        );

        // background images
        $('[style*=url]').filter(function() { return this.style.backgroundImage.indexOf('static.wixstatic.com') == -1 ? false : true }).each(function() {
            let link = $(this);
            // extract url from style
            let backgroundImage = this.style.backgroundImage;
            const reUrl = /.*url\s*\(\s*(.*)\s*\).*/i
            backgroundImage = backgroundImage.replace(reUrl, '$1');
            // remove leading & trailing quotes
            const src = backgroundImage.replace(/^['"]/, "").replace(/['"]+$/, "");
            const fullsize = src.replace(/(^.*?~mv2\..*?)\/.*/, '$1');
            if (fullsize != src) {
                link.data().hoverZoomSrc = [fullsize];
                res.push(link);
            }
        });

        callback($(res), this.name);
    }
});