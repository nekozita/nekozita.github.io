package XML;
#
# ＸＭＬ解析 モジュール
#

use strict;


#-------------------------------------------------
# コンストラクタ
sub new
{
	my $class = shift;
	my $self  = {@_};
	bless $self, $class;

	return $self;
}


#-------------------------------------------------
# 変換処理
sub convert
{
	my $self = shift;
	my $text = shift;

	my $flat = $self->_to_flat( $text );
	my $tree = $self->_to_tree( $flat, "" );

	return $tree;
}


#-------------------------------------------------
# フラット形式へ変換
sub _to_flat
{
	my $self = shift;
	my $text = shift;
	my $flat = [];
	my $tag;

	while ( $$text =~ /<(\?(.+?)\?|\!--(.*?)--|(.+?))>([^<]*)/sg )
	{
		my ( $match, $dec, $cmt, $elem, $follow ) = ( $1, $2, $3, $4, $5 );

		if ( $elem )
		{
			my $node = {};

			# タグ要素の取り出し
			$tag = ( split( ' ', $elem ) )[0];

			if ( $tag =~ s|^/||  )
			{
				$node->{'endTag'} = 1;
			}
			elsif ( $tag =~ s|/$|| )
			{
			}
			else
			{
				$node->{'startTag'} = 1;
			}

			$node->{'tagName'} = $tag;
			push( @$flat, $node );
		}

		if ( $follow )
		{
			push( @$flat, $follow );
		}
	}

	return $flat;
}


#-------------------------------------------------
# 木構造形式へ変換
sub _to_tree
{
	my $self   = shift;
	my $flat   = shift;
	my $parent = shift;
	my $tree   = {};
	my $text   = [];

	while ( @$flat )
	{
		my $node = shift @$flat;
		if ( !ref($node) )
		{
			push( @$text, $node );
			next;
		}

		my $name = $node->{'tagName'};
		if ( $node->{'endTag'} )
		{
			if ( $name eq $parent )
			{
				last;
			}
		}

		my $elem = {};
		if ( $node->{'startTag'} )
		{
			$elem = $self->_to_tree( $flat, $name );
		}

		$tree->{$name} ||= [];
		push( @{ $tree->{$name} }, $elem );
	}

	foreach ( keys %$tree )
	{
		next if ( @{ $tree->{$_} } > 1 );

		$tree->{$_} = shift @{ $tree->{$_} };
	}

	if( @$text == 1 )
	{
		$tree = shift @$text;
	}

	return $tree;
}


1;
